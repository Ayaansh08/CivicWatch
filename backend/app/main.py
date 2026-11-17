"""
Main entry point for the CivicWatch FastAPI application.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.platform.auth_router import router as auth_router
from backend.app.platform.admin_router import router as admin_router
from backend.app.citizen.router import router as citizen_router
from backend.app.geo.router import router as geo_router

# Ensure uploads directory exists
os.makedirs("backend/uploads", exist_ok=True)

# Create the FastAPI application instance.
app = FastAPI(title="CivicWatch API", version="1.0.0")

# Mount uploads directory for static file access
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# Allow the React frontend to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the application routers.
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(citizen_router)
app.include_router(geo_router)


@app.get("/health")
def health_check():
    """Return a simple status message."""
    return {"status": "ok"}
