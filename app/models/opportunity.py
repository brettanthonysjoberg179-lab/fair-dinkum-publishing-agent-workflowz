# app/models/opportunity.py
"""Opportunity scoring model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import Base


class OpportunityScore(Base):
    """Market opportunity scoring record."""
    __tablename__ = "opportunity_scores"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=False, index=True)
    keyword = Column(String, nullable=False)
    demand_score = Column(Float, nullable=True)
    competition_score = Column(Float, nullable=True)
    monetisation_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
