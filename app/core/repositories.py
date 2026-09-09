# app/core/repositories.py
"""Repository layer for database access."""
from app.core.database import session_scope
from app.models.project import Project, ProjectStatus
from app.models.opportunity import OpportunityScore
from app.models.outline import Outline, OutlineChapter
from app.models.manuscript import Manuscript, ManuscriptSection
from app.models.artifact import Artifact
import uuid
from datetime import datetime


class ProjectRepository:
    @staticmethod
    def create(project_id, title, niche, product_brief=None):
        with session_scope() as db:
            project = Project(
                id=project_id,
                title=title,
                niche=niche,
                product_brief=product_brief,
                status=ProjectStatus.DRAFT
            )
            db.add(project)
            db.flush()
            db.refresh(project)
            return project

    @staticmethod
    def get(project_id):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            return db.query(Project).filter(Project.id == project_id).first()
        finally:
            db.close()

    @staticmethod
    def update_status(project_id, status):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = status
                db.commit()
                db.refresh(project)
                return project
            return None
        finally:
            db.close()


class OpportunityRepository:
    @staticmethod
    def create(project_id, keyword, demand_score=None, competition_score=None,
               monetisation_score=None, overall_score=None, rationale=None):
        with session_scope() as db:
            score = OpportunityScore(
                id=str(uuid.uuid4()),
                project_id=project_id,
                keyword=keyword,
                demand_score=demand_score,
                competition_score=competition_score,
                monetisation_score=monetisation_score,
                overall_score=overall_score,
                rationale=rationale
            )
            db.add(score)
            db.flush()
            db.refresh(score)
            return score


class OutlineRepository:
    @staticmethod
    def create(project_id, title, description=None):
        with session_scope() as db:
            outline = Outline(
                id=str(uuid.uuid4()),
                project_id=project_id,
                title=title,
                description=description
            )
            db.add(outline)
            db.flush()
            db.refresh(outline)
            return outline

    @staticmethod
    def add_chapter(outline_id, title, summary=None, order=0):
        with session_scope() as db:
            chapter = OutlineChapter(
                id=str(uuid.uuid4()),
                outline_id=outline_id,
                title=title,
                summary=summary,
                order=order
            )
            db.add(chapter)
            db.flush()
            db.refresh(chapter)
            return chapter


class ManuscriptRepository:
    @staticmethod
    def create(project_id, title):
        with session_scope() as db:
            manuscript = Manuscript(
                id=str(uuid.uuid4()),
                project_id=project_id,
                title=title,
                status="draft",
                word_count=0
            )
            db.add(manuscript)
            db.flush()
            db.refresh(manuscript)
            return manuscript

    @staticmethod
    def add_section(manuscript_id, title, content=None, order=0):
        with session_scope() as db:
            section = ManuscriptSection(
                id=str(uuid.uuid4()),
                manuscript_id=manuscript_id,
                title=title,
                content=content,
                order=order,
                word_count=len(content.split()) if content else 0
            )
            db.add(section)
            db.flush()
            db.refresh(section)
            return section


class ArtifactRepository:
    @staticmethod
    def create(project_id, kind, path=None, url=None, size_bytes=None,
               mime_type=None, status="pending", metadata_json=None):
        with session_scope() as db:
            artifact = Artifact(
                id=str(uuid.uuid4()),
                project_id=project_id,
                kind=kind,
                path=path,
                url=url,
                size_bytes=size_bytes,
                mime_type=mime_type,
                status=status,
                metadata_json=metadata_json
            )
            db.add(artifact)
            db.flush()
            db.refresh(artifact)
            return artifact
