import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIReasoner:
    """
    Responsible for the core reasoning loop. 
    Constructs a prompt based on 'signals' and sends it to Gemini.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            print("Warning: GEMINI_API_KEY not found. AI Reasoner will return mock data.")
            self.model = None

    def reason(self, signals):
        """
        Sends signals to the LLM and retrieves the narrative explanation.
        """
        if not self.model:
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
            response = self.model.generate_content(prompt)
            # clean up potential markdown formatting from LLM
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"AI Error: {e}")
            return {
                "health_summary": "Error in AI processing",
                "explanation": str(e),
                "risk_assessment": "Manual check required"
            }
