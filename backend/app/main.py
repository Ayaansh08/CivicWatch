"""
Main entry point for the CivicWatch FastAPI application.
"""
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.platform.auth_router import router as auth_router
from backend.app.platform.admin_router import router as admin_router
from backend.app.citizen.router import router as citizen_router
from backend.app.geo.router import router as geo_router
from backend.app.authority.router import router as authority_router
from backend.app.platform.config import check_production_safety, get_cors_origins

# Raise immediately if production is running with the default secret key
check_production_safety()

# Ensure uploads directory exists
os.makedirs("backend/uploads", exist_ok=True)

# OpenAPI tag descriptions shown in the /docs page
_tags = [
    {
        "name": "auth",
        "description": "Register, log in, and retrieve the current user's profile.",
    },
    {
        "name": "admin",
        "description": "Admin-only management of departments, officers, and user roles.",
    },
    {
        "name": "complaints",
        "description": "File, view, and update citizen complaints.",
    },
    {
        "name": "authority",
        "description": "Authority dashboard for assigning, reviewing, and resolving complaints.",
    },
    {
        "name": "geo",
        "description": "Geospatial analytics: heatmaps, hotspots, and density reports.",
    },
]

# Create the FastAPI application instance with OpenAPI metadata
app = FastAPI(
    title="CivicWatch API",
    description=(
        "CivicWatch connects citizens with local government to resolve civic complaints. "
        "Citizens report issues, officers review and resolve them, and admins manage the system. "
        "All endpoints are authenticated with JWT Bearer tokens."
    ),
    version="1.0.0",
    openapi_tags=_tags,
)

# Mount uploads directory for static file access
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# Allow the React frontend to call this API — origins come from the environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to every HTTP response to reduce common browser attack vectors.
    nosniff stops MIME-type sniffing, DENY prevents iframe embedding, and
    no-referrer prevents leaking URLs to external sites.
    """
    response: Response = await call_next(request)
    # Prevent browsers from guessing the content type
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Prevent this page from being loaded inside an iframe
    response.headers["X-Frame-Options"] = "DENY"
    # Do not send the Referrer header to external sites
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


# Register the application routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(citizen_router)
app.include_router(geo_router)
# Register the authority router — adds /authority/* endpoints (CW-302+)
app.include_router(authority_router)


@app.get("/health", tags=["health"])
def health_check():
    """Return a simple status message to confirm the API is running."""
    return {"status": "ok"}
