"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.schemas import HealthResponse
from src.utils.database import Base, engine
from src.utils.security import ensure_encryption_key


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup: Create database tables and ensure encryption key
    Base.metadata.create_all(bind=engine)
    ensure_encryption_key()
    
    yield
    
    # Shutdown: Clean up resources
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A tool for managing PostgreSQL database connections and executing queries",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Application health status
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
    )


# Register API routers
from src.api import connections, queries, metadata, exports, nl2sql

app.include_router(connections.router, prefix="/api/connections", tags=["Connections"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["Metadata"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])
app.include_router(nl2sql.router, prefix="/api/nl2sql", tags=["NL2SQL"])
