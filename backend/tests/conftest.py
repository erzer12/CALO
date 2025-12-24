"""
Pytest configuration and fixtures for CALO backend tests.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing."""
    return {
        "city": "Udaipur",
        "source": "Mock",
        "forecast": [{
            "date": "2025-12-24",
            "temperature_celsius": 35,
            "condition": "Partly Cloudy",
            "rainfall_mm": 25
        }]
    }


@pytest.fixture
def sample_complaints_data():
    """Sample complaints data for testing."""
    import pandas as pd
    return pd.DataFrame({
        "category": ["sanitation", "sanitation", "infrastructure"],
        "description": ["Garbage not collected", "Drainage blocked", "Road damaged"]
    })


@pytest.fixture
def sample_trends_data():
    """Sample trends data for testing."""
    return {
        "fever udaipur": "Rising",
        "traffic udaipur": "Stable"
    }


@pytest.fixture
def sample_raw_data(sample_weather_data, sample_complaints_data, sample_trends_data):
    """Complete sample raw data for testing."""
    return {
        "weather": sample_weather_data,
        "complaints": sample_complaints_data,
        "trends": sample_trends_data,
        "news": [{"title": "Test News", "date": "2025-12-24", "category": "Local"}]
    }
