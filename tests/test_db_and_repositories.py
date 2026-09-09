# tests/test_db_and_repositories.py
"""Tests for database models and repositories."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, session_scope
from app.models.project import Project, ProjectStatus
from app.models.opportunity import OpportunityScore
from app.models.outline import Outline, OutlineChapter
from app.models.manuscript import Manuscript, ManuscriptSection
from app.models.artifact import Artifact
from app.core.repositories import (
    ProjectRepository, OpportunityRepository, OutlineRepository,
    ManuscriptRepository, ArtifactRepository
)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_project_repository_create_and_get():
    """Test creating and retrieving a project."""
    project = ProjectRepository.create(
        project_id='test-001',
        title='Test Ebook',
        niche='Test Niche',
        product_brief='Test brief'
    )
    
    fetched = ProjectRepository.get('test-001')
    assert fetched is not None
    assert fetched.title == 'Test Ebook'
    assert fetched.niche == 'Test Niche'
    assert fetched.status == ProjectStatus.DRAFT


def test_project_repository_update_status():
    """Test updating project status."""
    ProjectRepository.create(project_id='test-002', title='Test 2', niche='Niche 2')
    
    updated = ProjectRepository.update_status('test-002', ProjectStatus.RESEARCHING)
    assert updated.status == ProjectStatus.RESEARCHING
    
    fetched = ProjectRepository.get('test-002')
    assert fetched.status == ProjectStatus.RESEARCHING


def test_opportunity_repository():
    """Test creating opportunity scores."""
    score = OpportunityRepository.create(
        project_id='test-003',
        keyword='test keyword',
        demand_score=0.8,
        competition_score=0.3,
        monetisation_score=0.9,
        overall_score=0.75,
        rationale='Strong opportunity'
    )
    assert score.keyword == 'test keyword'
    assert score.overall_score == 0.75


def test_outline_repository():
    """Test creating outline and chapters."""
    outline = OutlineRepository.create(
        project_id='test-004',
        title='Test Outline',
        description='Test description'
    )
    
    chapter1 = OutlineRepository.add_chapter(
        outline_id=outline.id,
        title='Chapter 1',
        summary='First chapter',
        order=1
    )
    
    assert chapter1.title == 'Chapter 1'
    assert chapter1.order == 1


def test_manuscript_repository():
    """Test creating manuscript and sections."""
    manuscript = ManuscriptRepository.create(
        project_id='test-005',
        title='Test Manuscript'
    )
    
    section = ManuscriptRepository.add_section(
        manuscript_id=manuscript.id,
        title='Chapter 1',
        content='This is the first chapter content.',
        order=1
    )
    
    assert section.title == 'Chapter 1'
    assert section.word_count == 6


def test_artifact_repository():
    """Test creating artifacts."""
    artifact = ArtifactRepository.create(
        project_id='test-006',
        kind='cover',
        path='/tmp/cover.png',
        mime_type='image/png',
        size_bytes=1024,
        status='completed'
    )
    
    assert artifact.kind == 'cover'
    assert artifact.status == 'completed'


def test_all_models_have_tables():
    """Verify all models are registered in metadata."""
    table_names = Base.metadata.tables.keys()
    assert 'projects' in table_names
    assert 'opportunity_scores' in table_names
    assert 'outlines' in table_names
    assert 'outline_chapters' in table_names
    assert 'manuscripts' in table_names
    assert 'manuscript_sections' in table_names
    assert 'artifacts' in table_names
