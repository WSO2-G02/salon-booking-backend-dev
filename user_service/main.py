from fastapi import FastAPI
from api.v1.router import api_router

app = FastAPI(
    title="Salon Booking User Service",
    description="Handles user registration, authentication, and profiles.",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"}
