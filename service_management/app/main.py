"""
Service Management Microservice - Main Application
Manages salon services with admin-only access control.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path so we can import 'common'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from common.database import engine, Base
from app.routers import services

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Service Management API",
    description="Microservice for managing salon services (Admin only)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router)

@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "service": "Service Management API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

@app.post("/test/generate-token")
async def generate_test_token():
    """TEMPORARY: Generate test admin token for development"""
    from common.security import create_access_token
    from datetime import timedelta
    
    token_data = {
        "user_id": 1,
        "email": "admin@salon.com",
        "role": "admin"
    }
    
    token = create_access_token(token_data, expires_delta=timedelta(hours=24))
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": "24 hours",
        "note": "This is a test token. Remove this endpoint in production!"
    }    