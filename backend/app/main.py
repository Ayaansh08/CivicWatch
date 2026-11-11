"""
Main entry point for the CivicWatch FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.platform.auth_router import router as auth_router

# Create the FastAPI application instance
app = FastAPI(title="CivicWatch API", version="1.0.0")

# Allow the React frontend running on port 5173 to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the auth router — adds /auth/register, /auth/login, /auth/me
app.include_router(auth_router)


@app.get("/health")
def health_check():
    """Return a simple status message so teammates can confirm the API is running."""
    # Return a JSON object with status ok
    return {"status": "ok"}
