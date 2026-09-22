# app/api/server.py
"""Main MCP server entry point for the Fair Dinkum Publishing Agent Workforce.

This module sets up the FastAPI application, registers all agent routes,
and provides health-check and lifecycle endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import agent_router, metrics_router
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="Fair Dinkum Publishing Agent Workforce",
    description="MCP server orchestrating the end-to-end ebook production pipeline.",
    version="0.1.0",
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(agent_router, prefix="/agents", tags=["agents"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])

# Serve dashboard
DASHBOARD_HTML = os.path.join(BASE_DIR, "dashboard.html")
@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
def serve_dashboard():
    from fastapi.responses import HTMLResponse
    try:
        with open(DASHBOARD_HTML, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fair-dinkum-publishing-agent-workforce"}


@app.on_event("startup")
def startup_event():
    """Initialize resources on startup."""
    pass


@app.on_event("shutdown")
def shutdown_event():
    """Clean up resources on shutdown."""
    pass
