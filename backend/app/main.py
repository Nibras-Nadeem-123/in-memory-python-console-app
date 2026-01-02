"""
FastAPI application for SDD Phase 1 Backend.

Main entry point for the spec generation API.
"""

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.spec import router as spec_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SDD System Phase 1 API",
    description="""
    Spec-Driven Development System - Phase 1 Backend API

    Transforms natural language user intent into structured specifications.

    ## Features
    - Intent validation (50-500 words)
    - Entity extraction
    - Constraint identification
    - Assumption detection
    - Confidence scoring

    ## Non-Goals (Phase 1)
    - No persistence
    - No authentication
    - No planning or execution
    """,
    version="0.1.0",
    contact={
        "name": "SDD Development Team",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """
    Log all incoming requests and their processing time.

    Args:
        request: Incoming request
        call_next: Next middleware in chain

    Returns:
        Response from endpoint
    """
    start_time = time.time()

    # Log request
    logger.info(f"{request.method} {request.url.path} - Started")

    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"{request.method} {request.url.path} - Error: {str(e)}")
        raise

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Log application startup."""
    logger.info("SDD Phase 1 Backend API starting up...")
    logger.info("Version: 0.1.0")
    logger.info("Endpoints: /api/v1/spec (POST), /api/v1/health (GET)")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log application shutdown."""
    logger.info("SDD Phase 1 Backend API shutting down...")


# Register routers
app.include_router(spec_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        API metadata
    """
    return {
        "name": "SDD System Phase 1 API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "spec": "/api/v1/spec (POST)",
            "health": "/api/v1/health (GET)",
            "docs": "/docs",
        },
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle uncaught exceptions globally.

    Args:
        request: Request that caused exception
        exc: Exception that was raised

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
