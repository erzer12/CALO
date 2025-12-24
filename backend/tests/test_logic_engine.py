"""
Unit tests for LogicEngine - signal normalization and risk evaluation.
"""
import pytest
import pandas as pd
from src.services.logic_engine import LogicEngine
from src.config import settings


class TestSignalNormalization:
    """Tests for signal normalization logic."""
    
    def test_normalize_rainfall_stress(self):
        """Test rainfall stress normalization."""
        engine = LogicEngine()
        
        # Test with 25mm rainfall (half of critical threshold)
        data = {
            'weather': {'forecast': [{'rainfall_mm': 25, 'temperature_celsius': 25}]},
            'complaints': pd.DataFrame(),
            'trends': {}
        }
        signals = engine.normalize_signals(data)
        assert signals['weather_rainfall_stress'] == pytest.approx(25 / settings.RAINFALL_CRITICAL_MM)
    
    def test_normalize_heat_stress(self):
        """Test temperature stress normalization."""
        engine = LogicEngine()
        
        # Test with temperature above neutral
        data = {
            'weather': {'forecast': [{'rainfall_mm': 0, 'temperature_celsius': 35}]},
            'complaints': pd.DataFrame(),
            'trends': {}
        }
        signals = engine.normalize_signals(data)
        expected = (35 - settings.TEMP_NEUTRAL_C) / (settings.TEMP_MAX_C - settings.TEMP_NEUTRAL_C)
        assert signals['weather_heat_stress'] == pytest.approx(expected)
    
    def test_normalize_complaints_stress(self):
        """Test complaints normalization."""
        engine = LogicEngine()
        
        # Test with 3 sanitation complaints
        data = {
            'weather': {'forecast': [{'rainfall_mm': 0, 'temperature_celsius': 25}]},
            'complaints': pd.DataFrame({
                'category': ['sanitation', 'sanitation', 'sanitation']
            }),
            'trends': {}
        }
        signals = engine.normalize_signals(data)
        assert signals['complaints_sanitation_stress'] == pytest.approx(3 / settings.COMPLAINTS_CRITICAL)
    
    def test_normalize_health_anxiety(self):
        """Test social health anxiety normalization."""
        engine = LogicEngine()
        
        # Test with high fever trends
        data = {
            'weather': {'forecast': [{'rainfall_mm': 0, 'temperature_celsius': 25}]},
            'complaints': pd.DataFrame(),
            'trends': {'fever udaipur': 'spike'}
        }
        signals = engine.normalize_signals(data)
        assert signals['social_health_anxiety'] == 1.0


class TestRiskEvaluation:
    """Tests for risk evaluation logic."""
    
    def test_disease_risk_detection(self):
        """Test vector-borne disease risk detection."""
        engine = LogicEngine()
        
        signals = {
            'weather_rainfall_stress': 0.6,
            'complaints_sanitation_stress': 0.5,
            'social_health_anxiety': 0.8,
            'weather_condition_raw': 'Rainy'
        }
        
        result = engine.evaluate_risk(signals)
        active_risks = result['active_risks']
        
        # Should detect BIO_RISK
        risk_ids = [r['id'] for r in active_risks]
        assert 'BIO_RISK' in risk_ids
    
    def test_flood_risk_detection(self):
        """Test flood risk detection."""
        engine = LogicEngine()
        
        signals = {
            'weather_rainfall_stress': 0.9,
            'complaints_drainage_stress': 0.7,
            'weather_condition_raw': 'Heavy Rain'
        }
        
        result = engine.evaluate_risk(signals)
        active_risks = result['active_risks']
        
        # Should detect FLOOD_RISK
        risk_ids = [r['id'] for r in active_risks]
        assert 'FLOOD_RISK' in risk_ids
    
    def test_heat_risk_detection(self):
        """Test heatwave risk detection."""
        engine = LogicEngine()
        
        signals = {
            'weather_heat_stress': 0.8,
            'weather_condition_raw': 'Clear, Hot'
        }
        
        result = engine.evaluate_risk(signals)
        active_risks = result['active_risks']
        
        # Should detect HEAT_RISK
        risk_ids = [r['id'] for r in active_risks]
        assert 'HEAT_RISK' in risk_ids
    
    def test_no_risks_detected(self):
        """Test when no risks should be detected."""
        engine = LogicEngine()
        
        signals = {
            'weather_rainfall_stress': 0.1,
            'complaints_sanitation_stress': 0.1,
            'social_health_anxiety': 0.1,
            'weather_heat_stress': 0.2,
            'weather_condition_raw': 'Normal'
        }
        
        result = engine.evaluate_risk(signals)
        assert len(result['active_risks']) == 0
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        engine = LogicEngine()
        
        # All data sources present
        signals = {
            'weather_condition_raw': 'Rainy',
            'complaints_sanitation_stress': 0.3,
            'social_health_anxiety': 0.4
        }
        
        result = engine.evaluate_risk(signals)
        assert result['confidence_score'] == 1.0
        
        # Only weather present
        signals = {
            'weather_condition_raw': 'Rainy',
            'complaints_sanitation_stress': 0,
            'social_health_anxiety': 0
        }
        
        result = engine.evaluate_risk(signals)
        assert result['confidence_score'] == pytest.approx(1/3)
