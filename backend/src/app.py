from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.services.data_loader import DataLoader
from src.services.logic_engine import LogicEngine
from src.services.ai_reasoner import AIReasoner
from src.services.insight_formatter import InsightFormatter

# Initialize FastAPI app
app = FastAPI(title="CALO Backend", version="0.2")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services (Dependency Injection Pattern)
data_loader = DataLoader()
logic_engine = LogicEngine()
ai_reasoner = AIReasoner()
formatter = InsightFormatter()

@app.get("/")
def health_check():
    """Simple health check to verify backend is running."""
    return {"status": "CALO Backend Operational"}

@app.get("/analyze")
def analyze_city():
    """
    Main endpoint triggering the CALO reasoning loop.
    1. Load Data
    2. Normalize Signals (Logic Layer)
    3. Evaluate Risks (Logic Layer)
    4. Generate AI Reasoning (Decision Layer)
    5. Format Response
    """
    # Step 1: Load Data
    data = data_loader.load_latest_data()
    
    # Step 2: Logic Engine - Normalize & Evaluate
    normalized = logic_engine.normalize_signals(data)
    risk_assessment = logic_engine.evaluate_risk(normalized)
    
    # Step 3: Reason with AI (Passes the Risk Assessment + Protocol Context happens inside)
    insights = ai_reasoner.reason(risk_assessment)
    
    # Step 4: Format Response (Optional, sticking to AI output for now as check)
    # response = formatter.format(insights) 
    # For this architecture, AI Reasoner output IS the response structure we want.
    
    return insights
