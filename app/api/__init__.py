# app/api/__init__.py
"""FastAPI-based MCP server for the Fair Dinkum Publishing Agent Workforce."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as agent_router

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

# Stripe router
from fastapi import APIRouter
stripe_router = APIRouter()

@stripe_router.get("/products", tags=["stripe"])
def list_stripe_products():
    """List Stripe products."""
    from app.services.stripe import StripeService
    return StripeService.list_products()


@stripe_router.get("/stats", tags=["stripe"])
def get_stripe_stats():
    """Get Stripe account stats."""
    from app.services.stripe import StripeService
    return StripeService.get_stats()

app.include_router(stripe_router, prefix="/stripe", tags=["stripe"])


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