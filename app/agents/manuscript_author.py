# manuscript_author.py
from .base import BaseAgent
from app.core.repositories import ManuscriptRepository

class ManuscriptAuthorAgent(BaseAgent):
    def __init__(self, project_id):
        super().__init__(project_id)

    def execute(self, outline_data=None):
        self.update_status('Writing manuscript content')
        
        if not outline_data or 'chapters' not in outline_data:
            return {'status': 'error', 'message': 'No outline data provided for writing'}

        # Simulate LLM generating a manuscript based on the chapters
        # We use the first chapter's title or a generic one for the manuscript title
        title = f"Manuscript for {outline_data['chapters'][0]['title'] if outline_data['chapters'] else 'Project'}"
        
        manuscript_record = ManuscriptRepository.create(
            project_id=self.project_id,
            title=title
        )
        
        persisted_sections = []
        for i, ch in enumerate(outline_data['chapters']):
            # Simulate content generation
            content = f"This is the detailed content for chapter {i+1}: {ch['title']}. " \
                      f"It explores the key concepts in depth and provides actionable examples."
            
            section_record = ManuscriptRepository.add_section(
                manuscript_id=manuscript_record.id,
                title=ch['title'],
                content=content,
                order=i
            )
            persisted_sections.append({
                'id': section_record.id,
                'title': ch['title']
            })

        return {
            'status': 'success',
            'message': f'Manuscript written with {len(persisted_sections)} sections',
            'manuscript_id': manuscript_record.id,
            'sections': persisted_sections
        }
