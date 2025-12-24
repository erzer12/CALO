import pandas as pd
import json
import os
import logging
from datetime import datetime
import requests
import feedparser
from src.config.settings import USE_REAL_DATA, WEATHER_API_URL, NEWS_RSS_URL

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Responsible for ingesting raw data from various sources.
    Switches between local mock files and real APIs based on USE_REAL_DATA flag.
    """
    
    def __init__(self):
        # Define paths relative to valid execution context (usually backend/ root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # points to src
        self.data_dir = os.path.join(base_dir, 'data')

    def _load_json(self, filename):
        try:
            path = os.path.join(self.data_dir, filename)
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {filename}")
            return {}

    def _load_csv(self, filename):
        try:
            path = os.path.join(self.data_dir, filename)
            return pd.read_csv(path)
        except Exception as e:
            logger.warning(f"Could not read CSV {filename}: {e}")
            return pd.DataFrame()

    def _fetch_weather_api(self):
        """Fetches real weather from Open-Meteo API"""
        logger.info(f"Fetching weather from Open-Meteo API...")
        try:
            response = requests.get(WEATHER_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Map API response to our internal structure
            current = data.get('current_weather', {})
            daily = data.get('daily', {})
            
            return {
                "city": "Udaipur",
                "source": "Open-Meteo",
                "forecast": [
                    {
                        "date": current.get('time', 'Today')[:10],
                        "temperature_celsius": current.get('temperature'),
                        "condition": "Real data (Code: " + str(current.get('weathercode')) + ")",
                        "rainfall_mm": daily.get('precipitation_sum', [0])[0] if 'precipitation_sum' in daily else 0
                    }
                ]
            }
        except Exception as e:
            logger.warning(f"Weather API Error: {e}. Falling back to mock data.")
            return None

    def _fetch_news_rss(self):
        """Fetches real news from RSS feed"""
        logger.info(f"Fetching news from RSS feed...")
        try:
            feed = feedparser.parse(NEWS_RSS_URL)
            articles = []
            for entry in feed.entries[:5]: # Top 5 stories
                articles.append({
                    "title": entry.title,
                    "date": getattr(entry, 'published', 'Recently'),
                    "category": "General"
                })
            return articles
        except Exception as e:
            logger.warning(f"RSS feed error: {e}. Falling back to mock data.")
            return None

    def load_latest_data(self):
        """
        Fetches the most recent snapshot of city data.
        If USE_REAL_DATA is True, attempts to fetch from APIs.
        Falls back to local file mocks on failure.
        """
        # Default to mocks
        data = {
            "complaints": self._load_csv("udaipur_complaints.csv"),
            "trends": self._load_json("udaipur_trends.json"), # Trends still manual for MVP
            "weather": self._load_json("udaipur_weather.json"),
            "news": self._load_json("udaipur_news.json")
        }

        if USE_REAL_DATA:
            logger.info(">>> REAL DATA MODE ENABLED <<<")
            
            # 1. Weather
            real_weather = self._fetch_weather_api()
            if real_weather:
                data['weather'] = real_weather
            
            # 2. News
            real_news = self._fetch_news_rss()
            if real_news:
                data['news'] = real_news
                
            # 3. Complaints - Logic would go here to fetch from a portal if available
            # 4. Trends - Logic to scrape Google Trends if feasible
            
        return data
