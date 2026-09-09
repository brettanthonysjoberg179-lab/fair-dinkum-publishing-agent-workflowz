# tests/test_workflow.py
"""Tests for the workflow service."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
from app.services.workflow import WorkflowService
from app.models.project import ProjectStatus


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_workflow_service_initialization():
    """Test WorkflowService can be instantiated."""
    service = WorkflowService(project_id="test-workflow-001")
    assert service.project_id == "test-workflow-001"


def test_run_product_director():
    """Test the product director step."""
    service = WorkflowService(project_id="test-workflow-002")
    result = service.run_product_director(
        title="Test Ebook",
        niche="Test Niche",
        product_brief="Test brief"
    )
    assert result["project"] == "test-workflow-002"
    assert result["agent_result"]["status"] == "success"


def test_run_market_research():
    """Test the market research step."""
    service = WorkflowService(project_id="test-workflow-003")
    result = service.run_market_research(keywords=["ebook", "market"], depth=3)
    assert result["status"] == "success"
    assert result["keywords"] == ["ebook", "market"]


def test_run_opportunity_scoring():
    """Test the opportunity scoring step."""
    service = WorkflowService(project_id="test-workflow-004")
    result = service.run_opportunity_scoring()
    assert result["status"] == "success"


def test_run_positioning_offer():
    """Test the positioning offer step."""
    service = WorkflowService(project_id="test-workflow-005")
    result = service.run_positioning_offer()
    assert result["status"] == "success"


def test_run_outline_architect():
    """Test the outline architect step."""
    service = WorkflowService(project_id="test-workflow-006")
    result = service.run_outline_architect()
    assert result["status"] == "success"


def test_run_manuscript_author():
    """Test the manuscript author step."""
    service = WorkflowService(project_id="test-workflow-007")
    result = service.run_manuscript_author()
    assert result["status"] == "success"


def test_run_editorial():
    """Test the editorial step."""
    service = WorkflowService(project_id="test-workflow-008")
    result = service.run_editorial()
    assert result["status"] == "success"


def test_run_fact_check_compliance():
    """Test the fact check compliance step."""
    service = WorkflowService(project_id="test-workflow-009")
    result = service.run_fact_check_compliance()
    assert result["status"] == "success"


def test_run_cover_creative_director():
    """Test the cover creative director step."""
    service = WorkflowService(project_id="test-workflow-010")
    result = service.run_cover_creative_director()
    assert result["status"] == "success"


def test_run_ebook_production():
    """Test the ebook production step."""
    service = WorkflowService(project_id="test-workflow-011")
    result = service.run_ebook_production()
    assert result["status"] == "success"


def test_run_sales_copy():
    """Test the sales copy step."""
    service = WorkflowService(project_id="test-workflow-012")
    result = service.run_sales_copy()
    assert result["status"] == "success"


def test_run_funnel_fulfillment():
    """Test the funnel fulfillment step."""
    service = WorkflowService(project_id="test-workflow-013")
    result = service.run_funnel_fulfillment()
    assert result["status"] == "success"


def test_run_analytics_optimisation():
    """Test the analytics optimisation step."""
    service = WorkflowService(project_id="test-workflow-014")
    result = service.run_analytics_optimisation()
    assert result["status"] == "success"


def test_run_obsidian_knowledge_manager():
    """Test the obsidian knowledge manager step."""
    service = WorkflowService(project_id="test-workflow-015")
    result = service.run_obsidian_knowledge_manager()
    assert result["status"] == "success"


def test_run_launch_strategist():
    """Test the launch strategist step."""
    service = WorkflowService(project_id="test-workflow-016")
    result = service.run_launch_strategist()
    assert result["status"] == "success"
