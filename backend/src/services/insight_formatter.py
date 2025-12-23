class InsightFormatter:
    """
    Responsible for ensuring the output matches the strict JSON contract expected by the frontend.
    This acts as a serializer or adapter.
    """
    
    def format(self, ai_output):
        """
        Transforms raw AI output into the schema defined in /contract/api_response.json
        Input keys: health_summary, explanation, risk_assessment
        Output keys: status, summary, details, future
        """
        explanation_text = ai_output.get("explanation", "No details provided.")
        # naive split for details list
        details_list = [s.strip() for s in explanation_text.split('.') if s.strip()]

        return {
            "status": "Analysis Complete",
            "summary": ai_output.get("health_summary", "No summary available."),
            "details": details_list,
            "future": ai_output.get("risk_assessment", "No future prediction available.")
        }
