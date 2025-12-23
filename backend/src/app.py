from fastapi import FastAPI
from src.services.data_loader import DataLoader
from src.services.signal_builder import SignalBuilder
from src.services.ai_reasoner import AIReasoner
from src.services.insight_formatter import InsightFormatter

# Initialize FastAPI app
app = FastAPI(title="CALO Backend", version="0.1")

# Initialize Services (Dependency Injection Pattern)
data_loader = DataLoader()
signal_builder = SignalBuilder()
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
    2. Build Signals
    3. Generate AI Reasoning
    4. Format Response according to Contract
    """
    # Step 1: Load Data
    data = data_loader.load_latest_data()
    
    # Step 2: Build Signals
    signals = signal_builder.compute_signals(data)
    
    # Step 3: Reason with AI
    insights = ai_reasoner.reason(signals)
    
    # Step 4: Format Response
    response = formatter.format(insights)
    
    return response
