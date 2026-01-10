from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from sqlmodel import SQLModel

from .config import settings
from .db import engine, check_connection
from .api.todos import router as todos_router

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    On startup: Check database connection
    On shutdown: Close database connections
    """
    # Startup
    logger.info("Starting backend application...")
    SQLModel.metadata.create_all(engine)
    if not check_connection():
        logger.error("Database connection failed!")
        raise RuntimeError("Cannot connect to database")
    logger.info("Database connection successful")
    yield
    # Shutdown
    logger.info("Shutting down backend application...")
    engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Phase 2 Todo API",
    description="REST API for the Phase 2 Spec-Driven Todo System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(todos_router)


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if check_connection() else "disconnected"
    }


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Phase 2 Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.log_level == "DEBUG" else "An unexpected error occurred"
        }
    )

