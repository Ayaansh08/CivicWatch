"""
Main entry point for the CivicWatch FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.platform.auth_router import router as auth_router
from backend.app.citizen.router import router as citizen_router

# Create the FastAPI application instance.
app = FastAPI(title="CivicWatch API", version="1.0.0")

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
app.include_router(citizen_router)


@app.get("/health")
def health_check():
    """Return a simple status message."""
    return {"status": "ok"}
