# app/api/server.py
"""Main MCP server entry point for the Fair Dinkum Publishing Agent Workforce.

This module sets up the FastAPI application, registers all agent routes,
and provides health-check and lifecycle endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent_router

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
