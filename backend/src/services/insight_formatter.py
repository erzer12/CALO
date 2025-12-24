"""
Insight Formatter - Transforms AI output to match API contract schema.
"""
import logging
from src.models.schemas import AnalyzeResponse, CitizenView, EngineerView

logger = logging.getLogger(__name__)


class InsightFormatter:
    """
    Responsible for ensuring the output matches the strict JSON contract expected by the frontend.
    This acts as a serializer or adapter between AI Reasoner output and the API contract.
    """
    
    def format(self, ai_output, risk_assessment=None):
        """
        Transforms raw AI output into the schema defined in contract/response_schema.json
        
        Args:
            ai_output: Output from AIReasoner (citizen_view and engineer_view)
            risk_assessment: Output from LogicEngine (signals, active_risks, confidence_score)
        
        Returns:
            AnalyzeResponse: Formatted response matching the contract schema
        """
        try:
            # Extract views from AI output
            citizen_view_data = ai_output.get("citizen_view", {})
            engineer_view_data = ai_output.get("engineer_view", {})
            
            # Build CitizenView model
            citizen_view = CitizenView(
                status_headline=citizen_view_data.get("status_headline", "City Status Unknown"),
                visual_theme=citizen_view_data.get("visual_theme", "Normal")
            )
            
            # Build EngineerView model
            confidence = risk_assessment.get("confidence_score", 0.5) if risk_assessment else 0.5
            
            engineer_view = EngineerView(
                confidence_score=confidence,
                detected_risks=engineer_view_data.get("detected_risks", []),
                raw_signals=engineer_view_data.get("raw_signals", {}),
                logic_trace=engineer_view_data.get("logic_trace", "No analysis trace available."),
                recommended_actions=engineer_view_data.get("recommended_actions", []),
                data_sources=risk_assessment.get("signals", {}) if risk_assessment else None
            )
            
            # Determine overall status
            visual_theme = citizen_view.visual_theme
            if visual_theme == "Critical":
                status = "Critical"
            elif visual_theme == "Caution":
                status = "Warning"
            else:
                status = "Healthy"
            
            # Build summary and details from engineer view
            summary = citizen_view.status_headline
            
            # Build details list from detected risks and contributing factors
            details = []
            if risk_assessment and risk_assessment.get("active_risks"):
                for risk in risk_assessment["active_risks"]:
                    details.append(f"{risk['name']} (Severity: {risk['severity']:.2f})")
                    details.extend(risk.get("contributing_factors", []))
            else:
                details.append("No significant risks detected")
            
            # Build future prediction
            future = "Continued monitoring recommended. "
            if engineer_view.recommended_actions:
                future += "Recommended actions: " + ", ".join(engineer_view.recommended_actions[:2])
            else:
                future += "No urgent actions required at this time."
            
            # Create the response
            response = AnalyzeResponse(
                status=status,
                summary=summary,
                details=details,
                future=future,
                citizen_view=citizen_view,
                engineer_view=engineer_view
            )
            
            logger.debug("Successfully formatted AI output to contract schema")
            return response
            
        except Exception as e:
            logger.error(f"Error formatting insights: {e}", exc_info=True)
            # Return a fallback response
            return AnalyzeResponse(
                status="Unknown",
                summary="Analysis formatting error occurred",
                details=["Unable to format analysis results"],
                future="Please retry the analysis",
                citizen_view=CitizenView(
                    status_headline="System Error",
                    visual_theme="Caution"
                ),
                engineer_view=EngineerView(
                    confidence_score=0.0,
                    detected_risks=[],
                    raw_signals={},
                    logic_trace=f"Formatting error: {str(e)}",
                    recommended_actions=["Check system logs", "Retry analysis"]
                )
            )
