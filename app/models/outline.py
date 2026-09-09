# app/models/outline.py
"""Outline and chapter models."""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import Base


class Outline(Base):
    """Book-level outline record."""
    __tablename__ = "outlines"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    chapters = relationship("OutlineChapter", back_populates="outline", order_by="OutlineChapter.order")


class OutlineChapter(Base):
    """Single chapter within an outline."""
    __tablename__ = "outline_chapters"

    id = Column(String, primary_key=True, index=True)
    outline_id = Column(String, ForeignKey("outlines.id"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    outline = relationship("Outline", back_populates="chapters")
