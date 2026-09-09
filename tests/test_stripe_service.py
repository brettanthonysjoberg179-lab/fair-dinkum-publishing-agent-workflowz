# tests/test_stripe_service.py
"""Tests for Stripe payment service."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stripe import StripeService


def test_stripe_service_import():
    """Test StripeService can be imported."""
    assert StripeService is not None


def test_create_customer():
    """Test customer creation without live API."""
    result = StripeService.create_customer(
        email="test@example.com",
        name="Test User"
    )
    # Without a live key, this should fail gracefully
    assert "status" in result


def test_list_products():
    """Test product listing without live API."""
    result = StripeService.list_products()
    assert "status" in result


def test_get_stats():
    """Test stats retrieval without live API."""
    result = StripeService.get_stats()
    assert "status" in result
