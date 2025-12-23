import os
from dotenv import load_dotenv

load_dotenv()

CITY_NAME = os.getenv("CITY_NAME", "Udaipur")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Feature Flags
USE_REAL_DATA = os.getenv("USE_REAL_DATA", "False").lower() == "true"

# External APIs
# Udaipur Coordinates: 24.5854, 73.7125
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=24.5854&longitude=73.7125&current_weather=true&daily=precipitation_sum&timezone=Asia%2FKolkata"

# Example RSS Feed (Times of India - Jaipur/Rajasthan or similar)
NEWS_RSS_URL = "https://timesofindia.indiatimes.com/rssfeeds/3012535.cms" # Rajasthan News
