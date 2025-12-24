import os
from dotenv import load_dotenv

load_dotenv()

# Basic Settings
CITY_NAME = os.getenv("CITY_NAME", "Udaipur")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")

# CORS Configuration
# Parse comma-separated list of allowed origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"
).split(",")

# Feature Flags
USE_REAL_DATA = os.getenv("USE_REAL_DATA", "False").lower() == "true"

# Caching Configuration
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600" if ENVIRONMENT == "production" else "300"))

# Risk Detection Thresholds
RAINFALL_CRITICAL_MM = float(os.getenv("RAINFALL_CRITICAL_MM", "50"))
TEMP_NEUTRAL_C = float(os.getenv("TEMP_NEUTRAL_C", "25"))
TEMP_MAX_C = float(os.getenv("TEMP_MAX_C", "45"))
COMPLAINTS_CRITICAL = int(os.getenv("COMPLAINTS_CRITICAL", "5"))

# Risk Severity Thresholds
DISEASE_RISK_THRESHOLD = float(os.getenv("DISEASE_RISK_THRESHOLD", "0.4"))
FLOOD_RISK_THRESHOLD = float(os.getenv("FLOOD_RISK_THRESHOLD", "0.5"))
HEAT_RISK_THRESHOLD = float(os.getenv("HEAT_RISK_THRESHOLD", "0.6"))

# External APIs
# Udaipur Coordinates: 24.5854, 73.7125
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=24.5854&longitude=73.7125&current_weather=true&daily=precipitation_sum&timezone=Asia%2FKolkata"

# Example RSS Feed (Times of India - Jaipur/Rajasthan or similar)
NEWS_RSS_URL = "https://timesofindia.indiatimes.com/rssfeeds/3012535.cms"  # Rajasthan News
