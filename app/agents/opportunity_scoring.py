# opportunity_scoring.py
from .base import BaseAgent
from app.core.repositories import OpportunityRepository

class OpportunityScoringAgent(BaseAgent):
    def __init__(self, project_id, scoring_weights=None):
        super().__init__(project_id)
        self.scoring_weights = scoring_weights or {
            'demand': 0.4,
            'competition': 0.3,
            'monetisation': 0.3
        }

    def execute(self, market_data=None):
        self.update_status('Scoring market opportunities')
        if not market_data or 'research_data' not in market_data:
            return {'status': 'error', 'message': 'No market research data provided for scoring'}

        research_results = market_data['research_data']
        scored_opportunities = []

        for item in research_results:
            # Simulate scoring based on the research data
            demand = 80 if item['search_volume'] == 'high' else 50
            comp = 30 if item['competition'] == 'medium' else 70 # lower is better for competition? No, usually score is quality.
            # Let's assume higher score is better. Competition score = 100 - competition_intensity.
            comp_score = 70 if item['competition'] == 'medium' else 30
            monet = 60 # base
            
            overall = (demand * self.scoring_weights['demand']) + \
                      (comp_score * self.scoring_weights['competition']) + \
                      (monet * self.scoring_weights['monetisation'])
            
            rationale = f"High demand ({item['search_volume']}) and {item['competition']} competition for {item['keyword']}."
            
            # Persist to DB
            score_record = OpportunityRepository.create(
                project_id=self.project_id,
                keyword=item['keyword'],
                demand_score=demand,
                competition_score=comp_score,
                monetisation_score=monet,
                overall_score=overall,
                rationale=rationale
            )
            scored_opportunities.append({
                'id': score_record.id,
                'keyword': item['keyword'],
                'overall_score': overall
            })

        return {
            'status': 'success',
            'message': f'Scored {len(scored_opportunities)} opportunities',
            'scores': scored_opportunities,
            'best_opportunity': max(scored_opportunities, key=lambda x: x['overall_score']) if scored_opportunities else None
        }
