# app/services/workflow.py
"""End-to-end workflow orchestration service."""
from typing import Dict, Any, Optional
from app.core.repositories import (
    ProjectRepository, OpportunityRepository, OutlineRepository,
    ManuscriptRepository, ArtifactRepository
)
from app.models.project import ProjectStatus

# Import agents
from app.agents.product_director import ProductDirectorAgent
from app.agents.market_research import MarketResearchAgent
from app.agents.opportunity_scoring import OpportunityScoringAgent
from app.agents.positioning_offer import PositioningOfferAgent
from app.agents.outline_architect import OutlineArchitectAgent
from app.agents.manuscript_author import ManuscriptAuthorAgent
from app.agents.editorial import EditorialAgent
from app.agents.fact_check_compliance import FactCheckComplianceAgent
from app.agents.cover_creative_director import CoverCreativeDirectorAgent
from app.agents.ebook_production import EbookProductionAgent
from app.agents.sales_copy import SalesCopyAgent
from app.agents.funnel_fulfillment import FunnelFulfillmentAgent
from app.agents.analytics_optimisation import AnalyticsOptimisationAgent
from app.agents.obsidian_knowledge_manager import ObsidianKnowledgeManagerAgent
from app.agents.launch_strategist import LaunchStrategistAgent
from app.agents.cloud_archivist import CloudArchivistAgent


class WorkflowService:
    """Orchestrates the end-to-end ebook production workflow."""

    def __init__(self, project_id: str):
        self.project_id = project_id

    def run_product_director(self, title: str, niche: str, product_brief: str) -> Dict[str, Any]:
        """Step 1: Create/update project brief."""
        project = ProjectRepository.create(
            project_id=self.project_id,
            title=title,
            niche=niche,
            product_brief=product_brief
        )
        agent = ProductDirectorAgent(self.project_id, product_brief)
        result = agent.execute()
        return {"project": project.id, "agent_result": result}

    def run_market_research(self, keywords: list, depth: int = 3) -> Dict[str, Any]:
        """Step 2: Conduct market research."""
        agent = MarketResearchAgent(self.project_id, keywords=keywords, depth=depth)
        result = agent.execute()
        ProjectRepository.update_status(self.project_id, ProjectStatus.RESEARCHING)
        return result

    def run_opportunity_scoring(self, market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 3: Score opportunities."""
        agent = OpportunityScoringAgent(self.project_id, scoring_weights={})
        result = agent.execute(market_data)
        return result

    def run_positioning_offer(self, opportunity_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 4: Define positioning and offer."""
        agent = PositioningOfferAgent(self.project_id)
        result = agent.execute(opportunity_data)
        ProjectRepository.update_status(self.project_id, ProjectStatus.OUTLINING)
        return result

    def run_outline_architect(self, positioning_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 5: Design outline."""
        agent = OutlineArchitectAgent(self.project_id)
        result = agent.execute(positioning_data)
        return result

    def run_manuscript_author(self, outline_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 6: Write manuscript."""
        agent = ManuscriptAuthorAgent(self.project_id)
        result = agent.execute(outline_data)
        ProjectRepository.update_status(self.project_id, ProjectStatus.WRITING)
        return result

    def run_editorial(self, manuscript_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 7: Editorial review."""
        agent = EditorialAgent(self.project_id)
        result = agent.execute(manuscript_data)
        ProjectRepository.update_status(self.project_id, ProjectStatus.EDITING)
        return result

    def run_fact_check_compliance(self, manuscript_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 8: Fact check and compliance."""
        agent = FactCheckComplianceAgent(self.project_id)
        result = agent.execute(manuscript_data)
        return result

    def run_cover_creative_director(self, brief_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 9: Cover creative direction."""
        agent = CoverCreativeDirectorAgent(self.project_id)
        result = agent.execute(brief_data)
        return result

    def run_ebook_production(self, manuscript_data: Optional[Dict] = None,
                            cover_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 10: Produce ebook."""
        agent = EbookProductionAgent(self.project_id)
        result = agent.execute(manuscript_data, cover_data)
        ProjectRepository.update_status(self.project_id, ProjectStatus.PRODUCTION)
        return result

    def run_sales_copy(self, positioning_data: Optional[Dict] = None,
                      manuscript_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 11: Write sales copy."""
        agent = SalesCopyAgent(self.project_id)
        result = agent.execute(positioning_data, manuscript_data)
        return result

    def run_funnel_fulfillment(self, sales_copy_data: Optional[Dict] = None,
                              payment_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 12: Setup funnel and fulfillment."""
        agent = FunnelFulfillmentAgent(self.project_id)
        result = agent.execute(sales_copy_data, payment_config)
        return result

    def run_analytics_optimisation(self, funnel_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 13: Optimize analytics."""
        agent = AnalyticsOptimisationAgent(self.project_id)
        result = agent.execute(funnel_data)
        return result

    def run_obsidian_knowledge_manager(self, project_artifacts: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 14: Publish to Obsidian vault."""
        agent = ObsidianKnowledgeManagerAgent(self.project_id)
        result = agent.execute(project_artifacts)
        return result

    def run_launch_strategist(self, funnel_data: Optional[Dict] = None,
                             analytics_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Step 15: Launch strategy."""
        agent = LaunchStrategistAgent(self.project_id)
        result = agent.execute(funnel_data, analytics_data)
        ProjectRepository.update_status(self.project_id, ProjectStatus.LAUNCH)
        return result

    def run_cloud_archivist(self, artifact_paths: list, project_name: str) -> Dict[str, Any]:
        """Step 16: Sync to Cloud Drive."""
        agent = CloudArchivistAgent(self.project_id)
        result = agent.execute(artifact_paths=artifact_paths, project_name=project_name)
        return result

    def run_full_pipeline(self, title: str, niche: str, product_brief: str,
                             keywords: list, depth: int = 3) -> Dict[str, Any]:
        """Run the complete end-to-end workflow with proper data piping."""
        results = {}

        # Step 1: Product Director
        results['product_director'] = self.run_product_director(title, niche, product_brief)

        # Step 2: Market Research
        results['market_research'] = self.run_market_research(keywords, depth)

        # Step 3: Opportunity Scoring (Pass research data)
        results['opportunity_scoring'] = self.run_opportunity_scoring(results['market_research'])

        # Step 4: Positioning (Pass scoring data)
        results['positioning'] = self.run_positioning_offer(results['opportunity_scoring'])

        # Step 5: Outline (Pass positioning data)
        results['outline'] = self.run_outline_architect(results['positioning'])

        # Step 6: Manuscript (Pass outline data)
        results['manuscript'] = self.run_manuscript_author(results['outline'])

        # Step 7-8: Editorial & Fact Check (Pass manuscript data)
        results['editorial'] = self.run_editorial(results['manuscript'])
        results['fact_check'] = self.run_fact_check_compliance(results['manuscript'])

        # Step 9: Cover (Pass positioning/brief data)
        results['cover'] = self.run_cover_creative_director(results['positioning'])

        # Step 10: Ebook Production (Pass manuscript and cover data)
        results['ebook'] = self.run_ebook_production(
            manuscript_data=results['manuscript'], 
            cover_data=results['cover']
        )

        # Step 11: Sales Copy (Pass positioning and manuscript)
        results['sales_copy'] = self.run_sales_copy(
            positioning_data=results['positioning'], 
            manuscript_data=results['manuscript']
        )

        # Step 12: Funnel (Pass sales copy)
        results['funnel'] = self.run_funnel_fulfillment(results['sales_copy'])

        # Step 13: Analytics (Pass funnel data)
        results['analytics'] = self.run_analytics_optimisation(results['funnel'])

        # Step 14: Obsidian (Pass all artifacts)
        results['obsidian'] = self.run_obsidian_knowledge_manager(results)

        # Step 15: Launch (Pass funnel and analytics)
        results['launch'] = self.run_launch_strategist(
            funnel_data=results['funnel'], 
            analytics_data=results['analytics']
        )

        # Mark as completed
        ProjectRepository.update_status(self.project_id, ProjectStatus.COMPLETED)

        return {
            "project_id": self.project_id,
            "status": "completed",
            "results": results
        }
