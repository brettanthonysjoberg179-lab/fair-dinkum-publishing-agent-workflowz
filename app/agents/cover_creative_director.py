# cover_creative_director.py
from .base import BaseAgent
import subprocess
import json
import os
from pathlib import Path

class CoverCreativeDirectorAgent(BaseAgent):
    def __init__(self, project_id):
        super().__init__(project_id)

    def execute(self, brief_data=None):
        self.update_status('Generating final ebook cover')
        
        # Extract metadata from brief_data (which comes from PositioningAgent in the pipeline)
        # Based on PositioningOfferAgent: target_keyword, positioning_statement, offer
        title = "Untitled Ebook"
        author = "Unknown Author"
        genre = "Default"
        subtitle = ""

        if brief_data:
            # The positioning agent provides a 'target_keyword'
            kw = brief_data.get('target_keyword', 'General Topic')
            title = f"The Ultimate {kw} Mastery"
            # We don't have author in positioning_data, so we'd usually fetch from ProjectRepository
            # For now, we'll use a placeholder or try to get it from the project
            from app.core.repositories import ProjectRepository
            project = ProjectRepository.get(self.project_id)
            if project:
                # Assuming author might be in a metadata field or we use a default for now
                author = "Brett Sjoberg" 
            
            genre = "Business" # Default for this pipeline's context or infer from kw
            subtitle = brief_data.get('positioning_statement', '').split('.')[0]

        # Use the real Ebook Cover Agent CLI tool
        cli_cmd = [
            "python3", "/home/brettanthonysjoberg179/ebook-cover-agent/ebook_cover_agent.py",
            "create",
            "--title", title,
            "--author", author,
            "--genre", genre,
            "--subtitle", subtitle
        ]
        
        try:
            result = subprocess.run(cli_cmd, capture_output=True, text=True, check=True)
            cover_data = json.loads(result.stdout)
            
            return {
                'status': 'success',
                'message': 'Cover generated via EbookCoverAgent',
                'cover_path': cover_data.get('cover_path'),
                'metadata': cover_data
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Cover generation failed: {str(e)}",
                'details': e
            }
