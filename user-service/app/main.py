"""
Main FastAPI application for User Service.
This file configures and starts the web server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth
import sys
sys.path.append('../../')
from common.database import engine, Base

# Create database tables
# This creates all tables defined in models.py if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Salon Booking - User Service",
    description="Handles user registration, authentication, and profile management",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # Alternative documentation
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "User Service",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "service": "user-service",
        "database": "connected"  # In production, actually test DB connection
    }

# Run with: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload