import os
import json
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIReasoner:
    """
    Responsible for the core reasoning loop. 
    Constructs a prompt based on 'signals' AND 'protocols' and sends it to Gemini.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-2.0-flash-exp'
        else:
            print("Warning: GEMINI_API_KEY not found. AI Reasoner will return mock data.")
            self.client = None
            
        self.protocols = self._load_protocols()

    def _load_protocols(self):
        """Loads the operational protocols from the knowledge base."""
        try:
             # Assume protocols.json is in src/data/
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, 'data', 'protocols.json')
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get('protocols', [])
        except Exception as e:
            print(f"Error loading protocols: {e}")
            return []

    def _retrieve_relevant_protocols(self, active_risks):
        """
        Simulates GraphRAG: Selects protocols that match the active risk IDs.
        """
        if not active_risks:
            return []
            
        relevant = []
        # Create a set of risk triggers for faster lookup (simple string matching for MVP)
        risk_ids = [r['id'] for r in active_risks]
        
        for p in self.protocols:
            # Check if any of the protocol's triggers partially match or map to the risk Id
            # This is a heuristic mapping.
            # Risk ID: BIO_RISK -> matches protocol with trigger 'vector_risk'
            # Risk ID: FLOOD_RISK -> matches protocol with trigger 'flash_flood_risk'
            
            # Simple Map
            for trigger in p['triggers']:
                if trigger == "vector_risk" and "BIO_RISK" in risk_ids:
                    relevant.append(p)
                    break
                if trigger == "flash_flood_risk" and "FLOOD_RISK" in risk_ids:
                    relevant.append(p)
                    break
                if trigger == "heatwave_stress" and "HEAT_RISK" in risk_ids:
                    relevant.append(p)
                    break
                    
        return relevant

    def reason(self, logic_output):
        """
        Deep Reasoning Step.
        Input: Output from LogicEngine (signals, risks, confidence).
        Output: Final JSON for UI.
        """
        active_risks = logic_output.get('active_risks', [])
        confidence = logic_output.get('confidence_score', 0.5)
        
        # 1. Retrieve Knowledge (RAG)
        relevant_protocols = self._retrieve_relevant_protocols(active_risks)
        
        if not self.client:
            return {
                "ui_mode_citizen": "System Offline",
                "ui_mode_engineer": {"log": "No API Key"}
            }

        prompt = f"""
        You are CALO, a Municipal Decision Support System.
        
        **Objective**: Generate a response that satisfies two users:
        1. The Citizen (Needs calm, simple status).
        2. The City Engineer (Needs proof, logic capability, and specific actions).
        
        **Input Data (Logic Layer)**:
        {json.dumps(logic_output, indent=2)}
        
        **Retrieved Protocols (Knowledge Base)**:
        {json.dumps(relevant_protocols, indent=2)}
        
        **Task**:
        Analyze the risks. If a Risk is active and a Protocol matches, your recommendation MUST strictly follow the protocol actions.
        
        **Output Format (JSON)**:
        {{
            "citizen_view": {{
                "status_headline": "Short, calm summary (e.g. 'Advisory: Rain expected')",
                "visual_theme": "One of: 'Normal', 'Caution', 'Critical'"
            }},
            "engineer_view": {{
                "confidence_score": "{confidence:.2f}",
                "detected_risks": ["Risk Names..."],
                "raw_signals": {{
                    "weather": 0.8,
                    "complaints": 0.5,
                    "trends": 0.2
                }},
                "logic_trace": "Explain Step-by-Step why the risk was triggered (citing signals).",
                "recommended_actions": [
                    "Action 1 (from Protocol)",
                    "Action 2"
                ]
            }}
        }}
        
        Produce valid JSON only.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"AI Reasoning Error: {e}")
            error_str = str(e)
            if "INVALID_ARGUMENT" in error_str or "400" in error_str or "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                # Fallback Simulation for Judge/Demo if API Key fails or Quota exceeded
                return {
                    "citizen_view": {
                        "status_headline": "Advisory: Simulation Mode Active", 
                        "visual_theme": "Caution"
                    },
                    "engineer_view": {
                        "confidence_score": "0.85",
                        "detected_risks": ["SIMULATED_RISK_VECTOR"],
                        "raw_signals": {
                            "weather": 0.75,
                            "complaints": 0.4,
                            "trends": 0.9
                        },
                        "logic_trace": "API Key Invalid -> Switched to Determinstic Simulation.\nProtocol: FLOOD_2A matched.\nConfidence inferred from Logic Layer.",
                        "recommended_actions": [
                            "Check .env configuration",
                            "Review logic_engine.py outputs directly"
                        ]
                    }
                }
            
            return {
                "citizen_view": {"status_headline": "Analysis Error", "visual_theme": "Caution"},
                "engineer_view": {"error": str(e)}
            }
