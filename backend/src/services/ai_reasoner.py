import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIReasoner:
    """
    Responsible for the core reasoning loop. 
    Constructs a prompt based on 'signals' AND 'protocols' and sends it to Gemini.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Note: google-generativeai is deprecated but we'll use models/gemini-pro for v1beta API
            self.model = genai.GenerativeModel('models/gemini-pro')
            logger.info("Gemini AI initialized with models/gemini-pro")
        else:
            logger.warning("GEMINI_API_KEY not found. AI Reasoner will return mock data.")
            self.model = None
            
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
            logger.error(f"Error loading protocols: {e}", exc_info=True)
            return []

    def _retrieve_relevant_protocols(self, active_risks):
        """
        Retrieves protocols that match the active risk IDs.
        Uses the 'matches_risk_ids' field from protocols.json for explicit matching.
        """
        if not active_risks:
            return []
            
        relevant = []
        risk_ids = {r['id'] for r in active_risks}
        
        for protocol in self.protocols:
            # Check if protocol matches any of the active risks
            matches = protocol.get('matches_risk_ids', [])
            if any(risk_id in risk_ids for risk_id in matches):
                relevant.append(protocol)
                logger.debug(f"Matched protocol {protocol['id']} to active risks")
        
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
        
        if not self.model:
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
            if not self.model:
                raise Exception("Gemini API not configured")
            
            response = self.model.generate_content(prompt)
            
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"AI Reasoning Error: {e}", exc_info=True)
            error_str = str(e)
            
            # Fallback: Use real analyzed data instead of hardcoded simulation
            # This ensures we still provide value even when AI API is unavailable
            active_risks = logic_output.get('active_risks', [])
            signals = logic_output.get('signals', {})
            confidence = logic_output.get('confidence_score', 0.5)
            
            # Determine status based on actual risks
            if active_risks:
                risk_names = [r['name'] for r in active_risks]
                max_severity = max([r['severity'] for r in active_risks])
                
                if max_severity > 0.7:
                    visual_theme = "Critical"
                    status_headline = f"Alert: {len(active_risks)} risk(s) detected"
                else:
                    visual_theme = "Caution"
                    status_headline = f"Advisory: {len(active_risks)} risk(s) require attention"
            else:
                visual_theme = "Normal"
                status_headline = "City systems normal - AI analysis offline"
                risk_names = []
            
            # Get relevant protocols for actions
            relevant_protocols = self._retrieve_relevant_protocols(active_risks)
            recommended_actions = []
            for protocol in relevant_protocols:
                recommended_actions.extend(protocol.get('actions', []))
            
            # If no protocols matched, provide generic actions
            if not recommended_actions:
                if active_risks:
                    recommended_actions = [
                        "Monitor conditions closely",
                        "Review historical patterns for similar conditions",
                        "Prepare contingency protocols"
                    ]
                else:
                    recommended_actions = [
                        "Continue routine monitoring",
                        "Maintain current alert status"
                    ]
            
            # Build logic trace from actual data
            logic_trace = "AI API unavailable - Using rule-based analysis:\n"
            logic_trace += f"• Data sources active: {int(confidence * 3)}/3\n"
            logic_trace += f"• Weather stress: {signals.get('weather_rainfall_stress', 0):.2f} (rainfall), "
            logic_trace += f"{signals.get('weather_heat_stress', 0):.2f} (heat)\n"
            logic_trace += f"• Complaints stress: {signals.get('complaints_sanitation_stress', 0):.2f}\n"
            logic_trace += f"• Social anxiety: {signals.get('social_health_anxiety', 0):.2f}\n"
            
            if active_risks:
                logic_trace += f"\nDetected {len(active_risks)} risk(s):\n"
                for risk in active_risks:
                    logic_trace += f"• {risk['name']}: severity {risk['severity']:.2f}\n"
                    logic_trace += f"  Factors: {', '.join(risk.get('contributing_factors', []))}\n"
            
            return {
                "citizen_view": {
                    "status_headline": status_headline,
                    "visual_theme": visual_theme
                },
                "engineer_view": {
                    "confidence_score": f"{confidence:.2f}",
                    "detected_risks": risk_names,
                    "raw_signals": {
                        "weather": round(max(signals.get('weather_rainfall_stress', 0), 
                                           signals.get('weather_heat_stress', 0)), 2),
                        "complaints": round(signals.get('complaints_sanitation_stress', 0), 2),
                        "trends": round(signals.get('social_health_anxiety', 0), 2)
                    },
                    "logic_trace": logic_trace,
                    "recommended_actions": recommended_actions[:5]  # Limit to 5 actions
                }
            }

