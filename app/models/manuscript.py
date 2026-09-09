# app/models/manuscript.py
"""Manuscript and section models."""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import Base


class Manuscript(Base):
    """Book-level manuscript record."""
    __tablename__ = "manuscripts"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    word_count = Column(Integer, default=0)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sections = relationship("ManuscriptSection", back_populates="manuscript", order_by="ManuscriptSection.order")


class ManuscriptSection(Base):
    """Single manuscript section/chapter."""
    __tablename__ = "manuscript_sections"

    id = Column(String, primary_key=True, index=True)
    manuscript_id = Column(String, ForeignKey("manuscripts.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    manuscript = relationship("Manuscript", back_populates="sections")
