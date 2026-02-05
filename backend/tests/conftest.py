"""Shared Test Fixtures"""
import pytest


@pytest.fixture
def auth_headers() -> dict:
    """Headers with API key for authenticated endpoints."""
    return {"X-API-Key": "smart_ai_project", "Content-Type": "application/json"}
