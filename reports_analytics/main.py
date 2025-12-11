"""
Analytics Service - Main Application
FastAPI application for Salon Analytics and Reporting
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.routes import router
from app.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Salon Booking System - Analytics Service",
    description="Analytics, reporting, and business intelligence service for the salon booking system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with custom format"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": errors}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {}
        }
    )


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    
    # Verify database connection
    if db_manager.health_check():
        logger.info(f"Database '{settings.DB_NAME}' connection established successfully")
    else:
        logger.error(f"Failed to connect to database '{settings.DB_NAME}'")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "description": "Salon Analytics & Reporting Service"
    }


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check for Kubernetes probes. Returns 200 if service is running."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )