# tests/test_agents.py
"""Tests for the agent workforce."""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from app.agents.base import BaseAgent
from app.agents.product_director import ProductDirectorAgent
from app.agents.market_research import MarketResearchAgent
from app.agents.opportunity_scoring import OpportunityScoringAgent
from app.agents.analytics_optimisation import AnalyticsOptimisationAgent
from app.agents.cover_creative_director import CoverCreativeDirectorAgent
from app.agents.ebook_production import EbookProductionAgent
from app.agents.editorial import EditorialAgent
from app.agents.fact_check_compliance import FactCheckComplianceAgent
from app.agents.funnel_fulfillment import FunnelFulfillmentAgent
from app.agents.launch_strategist import LaunchStrategistAgent
from app.agents.sales_copy import SalesCopyAgent
from app.agents.cloud_archivist import CloudArchivistAgent
from app.agents.credentials_manager import CredentialsManagerAgent


def test_base_agent():
    """Test base agent creation."""
    agent = BaseAgent(project_id="test")
    assert agent.project_id == "test"
    assert agent.status == "initialized"


def test_product_director_agent():
    """Test ProductDirectorAgent."""
    agent = ProductDirectorAgent(project_id="test", product_brief="Test Brief")
    result = agent.execute()
    assert result["status"] == "success"
    assert "brief" in result["message"]


def test_market_research_agent():
    """Test MarketResearchAgent."""
    agent = MarketResearchAgent(project_id="test", keywords=["eBook"], depth=3)
    result = agent.execute()
    assert result["status"] == "success"


def test_opportunity_scoring_agent():
    """Test OpportunityScoringAgent."""
    agent = OpportunityScoringAgent(project_id="test", scoring_weights={})
    result = agent.execute()
    assert result["status"] == "success"


def test_analytic_optimisation_agent():
    """Test AnalyticsOptimisationAgent."""
    agent = AnalyticsOptimisationAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_cover_creative_director_agent():
    """Test CoverCreativeDirectorAgent."""
    agent = CoverCreativeDirectorAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_ebook_production_agent():
    """Test EbookProductionAgent."""
    agent = EbookProductionAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_editorial_agent():
    """Test EditorialAgent."""
    agent = EditorialAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_fact_check_compliance_agent():
    """Test FactCheckComplianceAgent."""
    agent = FactCheckComplianceAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_funnel_fulfillment_agent():
    """Test FunnelFulfillmentAgent."""
    agent = FunnelFulfillmentAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_launch_strategist_agent():
    """Test LaunchStrategistAgent."""
    agent = LaunchStrategistAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


def test_sales_copy_agent():
    """Test SalesCopyAgent."""
    agent = SalesCopyAgent(project_id="test")
    result = agent.execute()
    assert result["status"] == "success"


@patch('app.agents.cloud_archivist.GoogleDriveService')
def test_cloud_archivist_agent(mock_drive_service):
    """Test CloudArchivistAgent."""
    # Mock the Google Drive service
    mock_service = MagicMock()
    mock_drive_service.return_value = mock_service
    mock_service.create_folder.return_value = "mock_folder_id"
    mock_service.upload_file.return_value = "mock_file_id"
    
    agent = CloudArchivistAgent(project_id="test")
    
    # Create a temp file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    try:
        result = agent.execute(artifact_paths=[temp_path], project_name="Test Project")
        assert result["status"] == "success"
        assert result["project_folder_id"] == "mock_folder_id"
        assert len(result["uploaded_files"]) == 1
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_credentials_manager_agent():
    """Test CredentialsManagerAgent."""
    agent = CredentialsManagerAgent(project_id="test")
    
    # Test guide action
    result = agent.execute(action='guide')
    assert result["status"] == "success"
    assert "GOOGLE CLOUD" in result["guide"]
    assert "console.cloud.google.com" in result["guide"]
    
    # Test verify action with existing credentials file
    result = agent.execute(action='verify', file_path='credentials.json')
    assert result["status"] == "success"


def test_api_routes():
    """Test the API routes."""
    from app.api.routes import router, list_agents
    agents = list_agents()
    assert "agents" in agents
    assert agents["count"] == 15