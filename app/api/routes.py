# app/api/routes.py
"""Agent workflow routes for the Fair Dinkum Publishing Agent Workforce."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.core.repositories import ProjectRepository, OpportunityRepository
from app.models.project import ProjectStatus

router = APIRouter()


class AgentRequest(BaseModel):
    project_id: str
    action: str
    payload: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/", tags=["agents"])
def list_agents():
    """List all available agents."""
    agents = [
        "product_director", "market_research", "opportunity_scoring",
        "positioning_offer", "outline_architect", "manuscript_author",
        "editorial", "fact_check_compliance", "cover_creative_director",
        "ebook_production", "sales_copy", "funnel_fulfillment",
        "analytics_optimisation", "obsidian_knowledge_manager", "launch_strategist"
    ]
    return {"agents": agents, "count": len(agents)}


@router.post("/{agent_name}/execute", response_model=AgentResponse, tags=["agents"])
def execute_agent(agent_name: str, request: AgentRequest):
    """Execute a specific agent workflow step."""
    valid_agents = [
        "product_director", "market_research", "opportunity_scoring",
        "positioning_offer", "outline_architect", "manuscript_author",
        "editorial", "fact_check_compliance", "cover_creative_director",
        "ebook_production", "sales_copy", "funnel_fulfillment",
        "analytics_optimisation", "obsidian_knowledge_manager", "launch_strategist"
    ]

    if agent_name not in valid_agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    # In production, this would dispatch to the actual agent
    return AgentResponse(
        status="success",
        message=f"Agent '{agent_name}' executed for project '{request.project_id}'",
        data={"agent": agent_name, "project_id": request.project_id}
    )


@router.post("/projects", tags=["projects"])
def create_project(project_id: str, title: str, niche: str, product_brief: Optional[str] = None):
    """Create a new project."""
    project = ProjectRepository.create(
        project_id=project_id,
        title=title,
        niche=niche,
        product_brief=product_brief
    )
    return {
        "status": "success",
        "message": "Project created",
        "data": {
            "id": project.id,
            "title": project.title,
            "niche": project.niche,
            "status": project.status.value
        }
    }


@router.get("/projects/{project_id}", tags=["projects"])
def get_project(project_id: str):
    """Get project details."""
    project = ProjectRepository.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "status": "success",
        "data": {
            "id": project.id,
            "title": project.title,
            "niche": project.niche,
            "status": project.status.value,
            "product_brief": project.product_brief,
            "positioning_statement": project.positioning_statement,
            "outline": project.outline,
            "manuscript_path": project.manuscript_path,
            "cover_path": project.cover_path,
            "ebook_path": project.ebook_path,
            "sales_copy_path": project.sales_copy_path,
            "funnel_url": project.funnel_url,
            "stripe_payment_link": project.stripe_payment_link,
            "obsidian_note_path": project.obsidian_note_path,
            "created_at": str(project.created_at),
            "updated_at": str(project.updated_at),
            "version": project.version
        }
    }


@router.patch("/projects/{project_id}/status", tags=["projects"])
def update_project_status(project_id: str, status: str):
    """Update project status."""
    try:
        new_status = ProjectStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    project = ProjectRepository.update_status(project_id, new_status)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "status": "success",
        "message": f"Project status updated to {status}",
        "data": {"id": project.id, "status": project.status.value}
    }


# Stripe endpoints
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