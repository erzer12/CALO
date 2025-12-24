"""
Pydantic models for CALO API request/response validation.
Provides runtime validation, auto-generated API docs, and type safety.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class RiskInfo(BaseModel):
    """Information about a detected risk."""
    id: str = Field(..., description="Unique risk identifier (e.g., 'BIO_RISK')")
    name: str = Field(..., description="Human-readable risk name")
    severity: float = Field(..., ge=0.0, le=1.0, description="Risk severity score (0.0-1.0)")
    contributing_factors: List[str] = Field(..., description="Factors contributing to this risk")


class CitizenView(BaseModel):
    """Citizen-facing view: Simple, calm, actionable information."""
    status_headline: str = Field(..., description="Short, calm summary for citizens")
    visual_theme: str = Field(..., description="UI theme: 'Normal', 'Caution', or 'Critical'")


class EngineerView(BaseModel):
    """Engineer-facing view: Detailed diagnostics and reasoning."""
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in analysis")
    detected_risks: List[str] = Field(default_factory=list, description="List of detected risk names")
    raw_signals: Dict[str, float] = Field(default_factory=dict, description="Normalized signal values")
    logic_trace: str = Field(..., description="Step-by-step reasoning explanation")
    recommended_actions: List[str] = Field(default_factory=list, description="Protocol-based actions")
    data_sources: Optional[Dict[str, Any]] = Field(None, description="Metadata about data sources used")


class AnalyzeResponse(BaseModel):
    """
    Main response format for /analyze endpoint.
    Matches the contract schema in contract/response_schema.json
    """
    status: str = Field(..., description="High-level city status ('Healthy', 'Warning', 'Critical')")
    summary: str = Field(..., description="1-2 sentence narrative explanation")
    details: List[str] = Field(..., description="Supporting evidence and key observations")
    future: str = Field(..., description="AI prediction of what might happen next")
    
    # Extended views for different user types
    citizen_view: Optional[CitizenView] = Field(None, description="Citizen-facing information")
    engineer_view: Optional[EngineerView] = Field(None, description="Engineer-facing diagnostics")


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint."""
    status: str = Field(..., description="Overall system status")
    services: Dict[str, str] = Field(default_factory=dict, description="Status of dependent services")
    version: str = Field(default="0.2", description="API version")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Additional error details")
