# tests/test_stripe_routes.py
"""Tests for Stripe API routes."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_stripe_products_endpoint():
    """Test Stripe products listing endpoint."""
    response = client.get("/stripe/products")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_stripe_stats_endpoint():
    """Test Stripe stats endpoint."""
    response = client.get("/stripe/stats")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
