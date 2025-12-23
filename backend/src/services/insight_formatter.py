class InsightFormatter:
    """
    Responsible for ensuring the output matches the strict JSON contract expected by the frontend.
    This acts as a serializer or adapter.
    """
    
    def format(self, ai_output):
        """
        Transforms raw AI output into the schema defined in /contract/api_response.json
        """
        # TODO: Validate ai_output against schema
        # TODO: Format and return
        pass
