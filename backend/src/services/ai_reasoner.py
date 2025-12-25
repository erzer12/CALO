"""
AIReasoner with multiple AI provider support
Supports: Groq (recommended), Google Gemini
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Try importing AI providers
GROQ_AVAILABLE = False
GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    logger.info("Groq SDK available")
except ImportError:
    logger.warning("Groq SDK not available")

try:
    from google import genai
    GEMINI_AVAILABLE = True
    logger.info("Google Genai SDK available")
except ImportError:
    logger.warning("Google Genai SDK not available")


class AIReasoner:
    """
    Responsible for AI-powered reasoning with fallback support.
    Priority: Groq > Gemini > Rule-based fallback
    """
    
    def __init__(self):
        self.ai_provider = None
        self.model_name = None
        
        # Try Groq first (fastest, most reliable)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=groq_key)
                self.ai_provider = "groq"
                self.model_name = "llama-3.1-70b-versatile"  # Best free model
                logger.info(f"✅ Groq AI initialized - Model: {self.model_name}")
                logger.info("Rate limits: 30 req/min, 6000 req/day")
            except Exception as e:
                logger.error(f"Groq initialization failed: {e}")
        
        # Try Gemini as fallback
        if not self.ai_provider:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key and GEMINI_AVAILABLE:
                try:
                    self.client = genai.Client(api_key=gemini_key)
                    self.ai_provider = "gemini"
                    self.model_name = "gemini-2.0-flash-exp"  # Latest fast model
                    logger.info(f"✅ Gemini AI initialized - Model: {self.model_name}")
                    logger.info("Rate limits: 15 req/min, 1500 req/day")
                except Exception as e:
                    logger.error(f"Gemini initialization failed: {e}")
        
        if not self.ai_provider:
            logger.warning("⚠️ No AI provider available - Will use rule-based fallback")
            self.client = None
            
        self.protocols = self._load_protocols()

    def _load_protocols(self):
        """Loads the operational protocols from the knowledge base."""
        try:
            protocol_path = os.path.join(
                os.path.dirname(__file__), 
                "../data/protocols.json"
            )
            with open(protocol_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data.get('protocols', []))} protocols")
                return data.get('protocols', [])
        except FileNotFoundError:
            logger.error(f"protocols.json not found at {protocol_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing protocols.json: {e}")
            return []

    def _retrieve_relevant_protocols(self, active_risks: List[Dict]) -> List[Dict]:
        """
        Retrieves protocols matching detected risks using explicit risk ID mapping.
        """
        if not active_risks:
            return []
        
        risk_ids = [risk['id'] for risk in active_risks]
        logger.debug(f"Searching protocols for risk IDs: {risk_ids}")
        
        relevant = []
        for protocol in self.protocols:
            matches_risk_ids = protocol.get('matches_risk_ids', [])
            
            # Check if any active risk matches this protocol
            if any(risk_id in matches_risk_ids for risk_id in risk_ids):
                relevant.append(protocol)
                logger.debug(f"Matched protocol {protocol['id']} to active risks")
        
        return relevant

    def reason(self, logic_output: Dict) -> Dict[str, Any]:
        """
        Main reasoning function with multi-provider support.
        """
        active_risks = logic_output.get('active_risks', [])
        signals = logic_output.get('signals', {})
        confidence = logic_output.get('confidence_score', 0.5)
        
        # Retrieve relevant protocols
        relevant_protocols = self._retrieve_relevant_protocols(active_risks)
        
        if not self.client:
            # Use rule-based fallback
            return self._rule_based_analysis(active_risks, signals, confidence, relevant_protocols)
        
        # Build prompt
        prompt = self._build_prompt(active_risks, signals, confidence, relevant_protocols)
        
        try:
            if self.ai_provider == "groq":
                response = self._call_groq(prompt)
            elif self.ai_provider == "gemini":
                response = self._call_gemini(prompt)
            else:
                raise Exception("No AI provider configured")
            
            # Parse JSON from response
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"AI Reasoning Error ({self.ai_provider}): {e}", exc_info=True)
            # Fallback to rule-based
            return self._rule_based_analysis(active_risks, signals, confidence, relevant_protocols)

    def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Smart City AI analyst. Respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        text = response.choices[0].message.content
        # Clean markdown code blocks if present
        text = text.replace('```json', '').replace('```', '').strip()
        return text

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        text = response.text
        # Clean markdown code blocks
        text = text.replace('```json', '').replace('```', '').strip()
        return text

    def _build_prompt(self, active_risks, signals, confidence, protocols) -> str:
        """Build AI prompt"""
        risk_summary = "\n".join([
            f"- {r['name']} (severity: {r['severity']}, factors: {', '.join(r.get('contributing_factors', []))})"
            for r in active_risks
        ]) if active_risks else "No critical risks detected."
        
        protocol_summary = "\n".join([
            f"- {p['name']}: {', '.join(p.get('actions', [])[:2])}"
            for p in protocols[:3]
        ]) if protocols else "No specific protocols triggered."
        
        return f"""
Analyze this city intelligence data for Udaipur and provide JSON response.

**Current Signals:**
- Weather Stress: {signals.get('weather_rainfall_stress', 0):.2f} (rainfall), {signals.get('weather_heat_stress', 0):.2f} (heat)
- Sanitation Complaints: {signals.get('complaints_sanitation_stress', 0):.2f}
- Health Anxiety: {signals.get('social_health_anxiety', 0):.2f}

**Detected Risks:**
{risk_summary}

**Recommended Protocols:**
{protocol_summary}

**Analysis Confidence:** {confidence:.0%}

Provide response in this EXACT JSON format:
{{
  "citizen_view": {{
    "status_headline": "Brief 1-sentence status for citizens",
    "visual_theme": "Normal|Caution|Critical"
  }},
  "engineer_view": {{
    "confidence_score": "{confidence:.2f}",
    "detected_risks": ["risk1", "risk2"],
    "raw_signals": {{
      "weather": 0.0-1.0,
      "complaints": 0.0-1.0,
      "trends": 0.0-1.0
    }},
    "logic_trace": "Brief explanation of analysis",
    "recommended_actions": ["action1", "action2", "action3"]
  }}
}}

Respond with valid JSON only.
"""

    def _rule_based_analysis(self, active_risks, signals, confidence, protocols) -> Dict:
        """Fallback rule-based analysis using real data"""
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
        
        # Get actions from protocols
        recommended_actions = []
        for protocol in protocols:
            recommended_actions.extend(protocol.get('actions', []))
        
        if not recommended_actions:
            if active_risks:
                recommended_actions = [
                    "Monitor conditions closely",
                    "Review historical patterns",
                    "Prepare contingency protocols"
                ]
            else:
                recommended_actions = [
                    "Continue routine monitoring",
                    "Maintain current alert status"
                ]
        
        # Build logic trace
        logic_trace = f"Rule-based analysis (AI: {self.ai_provider or 'unavailable'}):\n"
        logic_trace += f"• Data sources: Real weather + RSS news\n"
        logic_trace += f"• Detected {len(active_risks)} risk(s)\n"
        
        if active_risks:
            for risk in active_risks:
                logic_trace += f"• {risk['name']}: severity {risk['severity']:.2f}\n"
        
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
                "recommended_actions": recommended_actions[:5]
            }
        }
