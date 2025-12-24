import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.services.data_loader import DataLoader
from src.services.logic_engine import LogicEngine
from src.services.ai_reasoner import AIReasoner
from src.services.insight_formatter import InsightFormatter
from src.models.schemas import AnalyzeResponse, HealthCheckResponse, ErrorResponse
from src.config.settings import ALLOWED_ORIGINS, LOG_LEVEL, ENVIRONMENT

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CALO Backend",
    version="0.2",
    description="City as a Living Organism - AI-powered city intelligence system"
)

# Configure CORS with security
# In development, allow all localhost origins for easier testing
if ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",  # Any localhost port
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
else:
    # Production: strict CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

# Initialize Services
logger.info(f"Initializing CALO services (Environment: {ENVIRONMENT})")
try:
    data_loader = DataLoader()
    logic_engine = LogicEngine()
    ai_reasoner = AIReasoner()
    formatter = InsightFormatter()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}", exc_info=True)
    raise


@app.get("/", response_model=HealthCheckResponse)
def health_check():
    """
    Health check endpoint with dependency status.
    Returns the operational status of the backend and its dependencies.
    """
    try:
        services_status = {
            "gemini_api": "connected" if ai_reasoner.client else "disconnected",
            "data_loader": "operational",
            "logic_engine": "operational"
        }
        
        logger.debug("Health check performed successfully")
        return HealthCheckResponse(
            status="CALO Backend Operational",
            services=services_status,
            version="0.2"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service health check failed")


@app.get("/api/v1/analyze", response_model=AnalyzeResponse)
def analyze_city():
    """
    Main analysis endpoint for CALO reasoning pipeline.
    
    Process:
    1. Load Data from various sources
    2. Normalize Signals (Logic Layer)
    3. Evaluate Risks (Logic Layer)
    4. Generate AI Reasoning (Decision Layer)
    5. Format Response
    
    Returns:
        AnalyzeResponse: Comprehensive city analysis with citizen and engineer views
    """
    try:
        logger.info("Starting city analysis...")
        
        # Step 1: Load Data
        logger.debug("Loading latest city data...")
        data = data_loader.load_latest_data()
        
        # Step 2: Logic Engine - Normalize
        logger.debug("Normalizing signals...")
        normalized = logic_engine.normalize_signals(data)
        
        # Step 3: Logic Engine - Evaluate Risks
        logger.debug("Evaluating risks...")
        risk_assessment = logic_engine.evaluate_risk(normalized)
        logger.info(f"Detected {len(risk_assessment.get('active_risks', []))} active risks")
        
        # Step 4: AI Reasoning
        logger.debug("Generating AI insights...")
        insights = ai_reasoner.reason(risk_assessment)
        
        # Step 5: Format Response to match contract schema
        logger.debug("Formatting response...")
        response = formatter.format(insights, risk_assessment)
        
        logger.info("City analysis completed successfully")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Analysis service temporarily unavailable. Please try again later."
        )


# Backward compatibility: Keep /analyze endpoint for existing integrations
@app.get("/analyze", response_model=AnalyzeResponse, include_in_schema=False)
def analyze_city_legacy():
    """
    Legacy endpoint for backward compatibility.
    Redirects to /api/v1/analyze functionality.
    """
    return analyze_city()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for uncaught errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc) if ENVIRONMENT == "development" else None
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
