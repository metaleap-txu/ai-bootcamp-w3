"""
Service layer for Natural Language to SQL conversion using OpenAI GPT-4.

This module provides:
- Natural language understanding of database queries
- Schema-aware SQL generation using metadata context
- Confidence assessment (high/medium/low) based on quality heuristics
- Warning generation for ambiguous or potentially problematic queries
- OpenAI API integration with JSON structured output
- Low temperature (0.2) for deterministic SQL generation

Architecture:
1. Fetch database schema from MetadataService (tables, columns, types)
2. Build context-rich prompt with schema information
3. Call OpenAI API with system prompt emphasizing PostgreSQL syntax
4. Parse JSON response (sql, explanation, confidence, warnings)
5. Apply quality assessment heuristics
6. Return validated response

Requires OPENAI_API_KEY environment variable for OpenAI API access.
"""
from typing import Tuple

from openai import OpenAI
from sqlalchemy.orm import Session

from src.models.connection import Connection
from src.schemas.nl2sql import NL2SQLResponse
from src.services.metadata_service import MetadataService
from src.config import settings


class NL2SQLService:
    """Service for converting natural language to SQL using OpenAI."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.metadata_service = MetadataService(db)
    
    async def generate_sql(
        self, connection_id: int, natural_language: str
    ) -> NL2SQLResponse:
        """
        Generate SQL from natural language description.
        
        Args:
            connection_id: Connection ID for schema context
            natural_language: Natural language description
            
        Returns:
            NL2SQLResponse: Generated SQL with explanation and confidence
            
        Raises:
            ValueError: If connection not found or OpenAI key not configured
        """
        # Validate OpenAI API key
        settings.validate_openai_key()
        
        # Get connection
        connection = self.db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise ValueError(f"Connection with ID {connection_id} not found")
        
        # Get database schema context
        schema_context = await self._build_schema_context(connection_id)
        
        # Build prompt
        prompt = self._build_prompt(natural_language, schema_context, connection.database)
        
        # Call OpenAI API
        client = OpenAI(api_key=settings.openai_api_key)
        
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a PostgreSQL expert. Generate SQL queries from natural language. "
                            "Return ONLY valid PostgreSQL SELECT statements. "
                            "Always use proper table/column names from the provided schema. "
                            "Format your response as JSON with keys: sql, explanation, confidence (high/medium/low), warnings (optional)."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,  # Low temperature for more deterministic output
                response_format={"type": "json_object"},
            )
            
            # Parse response
            result = response.choices[0].message.content
            import json
            parsed = json.loads(result)
            
            # Determine confidence and warnings
            confidence, warnings = self._assess_quality(
                parsed.get("sql", ""),
                natural_language,
                schema_context,
            )
            
            return NL2SQLResponse(
                sql=parsed.get("sql", ""),
                explanation=parsed.get("explanation", "Generated SQL query"),
                confidence=parsed.get("confidence", confidence),
                warnings=parsed.get("warnings") or warnings,
            )
        except Exception as e:
            raise ValueError(f"OpenAI API error: {str(e)}") from e
    
    async def _build_schema_context(self, connection_id: int) -> str:
        """
        Build schema context string for OpenAI prompt.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            str: Schema context with tables and columns
        """
        try:
            # Get all schemas
            schemas = await self.metadata_service.get_schemas(connection_id)
            
            context_parts = []
            
            for schema in schemas[:5]:  # Limit to first 5 schemas to avoid token limits
                # Get tables for schema
                tables = await self.metadata_service.get_tables(connection_id, schema.name)
                
                for table in tables[:20]:  # Limit to 20 tables per schema
                    # Get table details
                    details = await self.metadata_service.get_table_details(
                        connection_id, schema.name, table.name
                    )
                    
                    # Format table info
                    columns_str = ", ".join(
                        f"{col.name} ({col.data_type})" for col in details.columns[:15]
                    )
                    context_parts.append(
                        f"Table: {schema.name}.{table.name}\n"
                        f"Columns: {columns_str}"
                    )
            
            if not context_parts:
                return "No schema information available."
            
            return "\n\n".join(context_parts)
        except Exception as e:
            return f"Error fetching schema: {str(e)}"
    
    def _build_prompt(
        self, natural_language: str, schema_context: str, database_name: str
    ) -> str:
        """
        Build OpenAI prompt with schema context.
        
        Args:
            natural_language: User's natural language query
            schema_context: Database schema information
            database_name: Database name
            
        Returns:
            str: Complete prompt for OpenAI
        """
        return f"""Database: {database_name}

Schema Information:
{schema_context}

User Request: {natural_language}

Generate a PostgreSQL SELECT query for this request. Return JSON with:
- sql: The SQL query (SELECT only)
- explanation: Brief explanation of what the query does
- confidence: "high", "medium", or "low" based on schema match
- warnings: Any caveats or assumptions (optional)

Important:
- Use ONLY tables and columns from the schema above
- Always use SELECT statements (no INSERT, UPDATE, DELETE, DROP)
- Use proper PostgreSQL syntax
- Include appropriate WHERE, JOIN, ORDER BY clauses as needed
- If the request is ambiguous, make reasonable assumptions and note them in warnings
"""
    
    def _assess_quality(
        self, sql: str, natural_language: str, schema_context: str
    ) -> Tuple[str, str | None]:
        """
        Assess the quality of generated SQL.
        
        Args:
            sql: Generated SQL
            natural_language: Original request
            schema_context: Schema context used
            
        Returns:
            Tuple[str, str | None]: (confidence level, warnings)
        """
        warnings = []
        
        # Check if SQL is empty
        if not sql.strip():
            return "low", "No SQL generated"
        
        # Check if it's a SELECT statement
        if not sql.strip().upper().startswith("SELECT"):
            warnings.append("Generated SQL is not a SELECT statement")
        
        # Check for common issues
        if "*" in sql and len(natural_language.split()) < 5:
            warnings.append("Using SELECT * - consider specifying exact columns")
        
        if "LIMIT" not in sql.upper():
            warnings.append("No LIMIT clause - query may return many rows")
        
        # Determine confidence
        if warnings:
            confidence = "medium" if len(warnings) == 1 else "low"
        else:
            confidence = "high"
        
        return confidence, "; ".join(warnings) if warnings else None
