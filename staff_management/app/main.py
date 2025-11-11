from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routers import staff
import sys
sys.path.append('../../')

from common.database import Base, engine
import asyncio

from app.security.authentication import AuthenticationError

print("Creating all database tables...")

# Initialize FastAPI app
app = FastAPI(
    title="Staff Management Microservice",
    description="Handles staff profiles, availability, and specialties",
    version="1.0.0"
)

#custom error handler for authentication failures
@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication failed",
            "message": str(exc),
            "path": request.url.path
        },
    )

# Async function to create tables
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Connected to Azure SQL Database successfully!")


# Run on startup
@app.on_event("startup")
async def on_startup():
    await init_models()


# Include all routes
app.include_router(staff.router)


# Root endpoint
@app.get("/")
def root():
    return {"message": "Staff Management Service Running", "docs": "/docs"}
