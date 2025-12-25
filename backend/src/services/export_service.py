"""
Service layer for exporting query results to various formats.

Supported formats:
- CSV: Comma-separated values using pandas DataFrame.to_csv()
- JSON: Array of objects with proper type serialization
- Excel: XLSX format using openpyxl engine via pandas

Features:
- Column header preservation
- NULL value handling
- Type-aware serialization (dates, numbers, booleans)
- Memory-efficient processing via StringIO/BytesIO buffers
- No intermediate file creation

All exports return bytes for streaming response with Content-Disposition headers.
"""
import io
import json
from typing import List, Any

import pandas as pd


class ExportService:
    """Service for exporting query results to various formats."""
    
    @staticmethod
    def export_to_csv(columns: List[str], rows: List[List[Any]]) -> bytes:
        """
        Export query results to CSV format.
        
        Args:
            columns: Column names
            rows: Row data
            
        Returns:
            bytes: CSV file content
        """
        df = pd.DataFrame(rows, columns=columns)
        
        # Export to CSV bytes
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode('utf-8')
    
    @staticmethod
    def export_to_json(columns: List[str], rows: List[List[Any]]) -> bytes:
        """
        Export query results to JSON format.
        
        Args:
            columns: Column names
            rows: Row data
            
        Returns:
            bytes: JSON file content
        """
        # Convert rows to list of dictionaries
        data = []
        for row in rows:
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            data.append(row_dict)
        
        # Export to JSON bytes
        json_str = json.dumps(data, indent=2, default=str)
        return json_str.encode('utf-8')
    
    @staticmethod
    def export_to_excel(columns: List[str], rows: List[List[Any]]) -> bytes:
        """
        Export query results to Excel format.
        
        Args:
            columns: Column names
            rows: Row data
            
        Returns:
            bytes: Excel file content
        """
        df = pd.DataFrame(rows, columns=columns)
        
        # Export to Excel bytes
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Query Results')
        
        excel_buffer.seek(0)
        return excel_buffer.read()
