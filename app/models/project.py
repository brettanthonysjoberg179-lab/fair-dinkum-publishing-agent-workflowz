# app/models/project.py
"""Core project model for the Fair Dinkum Publishing Agent Workforce."""
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum, Integer
from sqlalchemy.sql import func
import enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    OUTLINING = "outlining"
    WRITING = "writing"
    EDITING = "editing"
    PRODUCTION = "production"
    LAUNCH = "launch"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    """Master project record for an ebook product."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    niche = Column(String, nullable=False)
    status = Column(SAEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    product_brief = Column(Text, nullable=True)
    positioning_statement = Column(Text, nullable=True)
    outline = Column(Text, nullable=True)
    manuscript_path = Column(String, nullable=True)
    cover_path = Column(String, nullable=True)
    ebook_path = Column(String, nullable=True)
    sales_copy_path = Column(String, nullable=True)
    funnel_url = Column(String, nullable=True)
    stripe_payment_link = Column(String, nullable=True)
    obsidian_note_path = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, default=1, nullable=False)
