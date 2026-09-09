# app/models/artifact.py
"""Artifact model for generated ebook assets."""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import Base


class Artifact(Base):
    """Generated asset record: covers, EPUB, PDF, HTML flipbook, sales page, etc."""
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=False, index=True)
    kind = Column(String, nullable=False)
    path = Column(String, nullable=True)
    url = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
