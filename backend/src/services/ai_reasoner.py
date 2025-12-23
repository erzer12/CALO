import os
import json
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIReasoner:
    """
    Responsible for the core reasoning loop. 
    Constructs a prompt based on 'signals' and sends it to Gemini via the new SDK.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            # New SDK Initialization
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-2.0-flash-exp'
        else:
            print("Warning: GEMINI_API_KEY not found. AI Reasoner will return mock data.")
            self.client = None

    def reason(self, signals):
        """
        Sends signals to the LLM and retrieves the narrative explanation.
        """
        if not self.client:
            return {
                "health_summary": "System running in offline mode. Signals detected: " + str(signals),
                "explanation": "No API key provided, skipping AI reasoning.",
                "risk_assessment": "Unknown"
            }

        prompt = f"""
        You are CALO, the City AI for Udaipur. 
        Analyze the following city signals and provide a status report.
        
        Signals:
        {json.dumps(signals, indent=2)}
        
        Return valid JSON with exactly these keys:
        - health_summary: A concise, non-technical statement on the city's current health.
        - explanation: Explain WHY these issues are emerging (cite specific signals like rainfall or fever trends). Keep it simple.
        - risk_assessment: what might happen next if trends continue?
        
        Do not use markdown formatting (no ```json), just plain text JSON.
        """
        
        try:
            # New SDK call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # clean up potential markdown formatting from LLM
            # The new SDK response object also has a .text property
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"AI Error: {e}")
            return {
                "health_summary": "Error in AI processing",
                "explanation": str(e),
                "risk_assessment": "Manual check required"
            }
