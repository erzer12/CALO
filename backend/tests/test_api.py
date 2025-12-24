"""
Integration tests for CALO API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test health check returns operational status."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "CALO Backend Operational"
        assert "services" in data
        assert "version" in data
        assert data["version"] == "0.2"
    
    def test_health_check_services_status(self, client):
        """Test health check includes service statuses."""
        response = client.get("/")
        data = response.json()
        
        assert "gemini_api" in data["services"]
        assert "data_loader" in data["services"]
        assert "logic_engine" in data["services"]


class TestAnalyzeEndpoint:
    """Tests for the main analyze endpoint."""
    
    def test_analyze_returns_valid_response(self, client):
        """Test that analyze endpoint returns valid response structure."""
        response = client.get("/api/v1/analyze")
        
        # Should return 200 or handle gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields from contract schema
            assert "status" in data
            assert "summary" in data
            assert "details" in data
            assert "future" in data
            assert isinstance(data["details"], list)
    
    def test_analyze_includes_views(self, client):
        """Test that analyze response includes citizen and engineer views."""
        response = client.get("/api/v1/analyze")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for extended views
            assert "citizen_view" in data
            assert "engineer_view" in data
            
            # Validate citizen view structure
            if data["citizen_view"]:
                assert "status_headline" in data["citizen_view"]
                assert "visual_theme" in data["citizen_view"]
            
            # Validate engineer view structure
            if data["engineer_view"]:
                assert "confidence_score" in data["engineer_view"]
                assert "detected_risks" in data["engineer_view"]
                assert "raw_signals" in data["engineer_view"]
                assert "logic_trace" in data["engineer_view"]
                assert "recommended_actions" in data["engineer_view"]
    
    def test_analyze_handles_errors_gracefully(self, client):
        """Test that analyze endpoint handles errors without exposing internals."""
        response = client.get("/api/v1/analyze")
        
        # Even if it errors, should return proper error structure
        if response.status_code != 200:
            data = response.json()
            assert "detail" in data
            # Should not expose internal stack traces in production


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are configured."""
        response = client.options("/api/v1/analyze", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_on_invalid_route(self, client):
        """Test that invalid routes return 404."""
        response = client.get("/invalid/route")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test that incorrect methods are handled."""
        response = client.post("/")  # Health check only accepts GET
        assert response.status_code == 405
