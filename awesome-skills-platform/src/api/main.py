"""
FastAPI main application.
"""
import logging
import time
import traceback
from typing import Callable
from uuid import uuid4

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.core.config import settings
from src.api.routers import agents, skills, mcp, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Agent Platform API with Strands Agents and AWS Bedrock AgentCore",
)


# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Callable):
    """Log request details and response time."""
    request_id = str(uuid4())[:8]
    start_time = time.time()

    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}"
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.3f}s"
        )
        raise


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with logging."""
    logger.warning(
        f"HTTP {exc.status_code} - {request.method} {request.url.path} - {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error - {request.method} {request.url.path} - {exc.error_count()} errors"
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(
        f"Unhandled exception - {request.method} {request.url.path} - {type(exc).__name__}: {str(exc)}"
    )
    if settings.debug:
        logger.error(f"Traceback:\n{traceback.format_exc()}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


# Include routers
app.include_router(agents.router, prefix=settings.api_prefix)
app.include_router(skills.router, prefix=settings.api_prefix)
app.include_router(mcp.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Agent Platform API",
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/health",
    }
