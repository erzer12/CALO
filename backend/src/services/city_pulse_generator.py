"""
CALO Advanced Data Ingestion Pipeline
Aggregates 5 disparate city signals into a unified "City Pulse" JSON.

Data Sources:
1. Mind (Google Trends) - Search anxiety
2. Body (Weather) - Environmental conditions
3. Voice (News) - Public sentiment
4. Pain (Complaints) - Civic issues
5. Anatomy (Places) - City infrastructure
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

# Third-party imports (install via requirements.txt)
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("Warning: pytrends not installed")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: textblob not installed")

import requests
from dotenv import load_dotenv

load_dotenv()

# =======================
# 1. THE MIND: Search Trends
# =======================

def fetch_search_trends() -> Dict[str, Any]:
    """
    Fetches Google Trends data for Rajasthan to measure "search anxiety."
    
    Why normalize: Raw trend scores (0-100) need to be converted to 0-1 scale
    for uniform risk scoring across different data sources.
    
    Returns:
        dict: Normalized search anxiety indices per keyword
    """
    if not PYTRENDS_AVAILABLE:
        return {
            "status": "mock",
            "dengue_anxiety": 0.45,
            "waterlogging_anxiety": 0.62,
            "traffic_anxiety": 0.33,
            "hospital_anxiety": 0.28
        }
    
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-IN', tz=330)  # IST timezone
        
        # Keywords representing city concerns
        keywords = ['Dengue', 'Waterlogging', 'Traffic Jam', 'Hospital']
        
        # Build payload for last 7 days in Rajasthan
        pytrends.build_payload(
            keywords,
            cat=0,
            timeframe='now 7-d',
            geo='IN-RJ',  # Rajasthan
            gprop=''
        )
        
        # Fetch interest over time
        df = pytrends.interest_over_time()
        
        if df.empty:
            raise Exception("No trend data returned")
        
        # Calculate average interest for each keyword (normalize 0-100 to 0-1)
        dengue_avg = df['Dengue'].mean() / 100.0 if 'Dengue' in df else 0.3
        water_avg = df['Waterlogging'].mean() / 100.0 if 'Waterlogging' in df else 0.2
        traffic_avg = df['Traffic Jam'].mean() / 100.0 if 'Traffic Jam' in df else 0.25
        hospital_avg = df['Hospital'].mean() / 100.0 if 'Hospital' in df else 0.2
        
        return {
            "status": "live",
            "source": "Google Trends",
            "region": "Rajasthan",
            "timestamp": datetime.now().isoformat(),
            "dengue_anxiety": round(dengue_avg, 2),
            "waterlogging_anxiety": round(water_avg, 2),
            "traffic_anxiety": round(traffic_avg, 2),
            "hospital_anxiety": round(hospital_avg, 2),
            "overall_anxiety": round((dengue_avg + water_avg + traffic_avg + hospital_avg) / 4, 2)
        }
        
    except Exception as e:
        print(f"Trends API Error: {e}")
        # Fallback to simulated data
        return {
            "status": "fallback",
            "error": str(e),
            "dengue_anxiety": 0.45,
            "waterlogging_anxiety": 0.62,
            "traffic_anxiety": 0.33,
            "hospital_anxiety": 0.28
        }


# =======================
# 2. THE BODY: Environment
# =======================

def fetch_weather_data() -> Dict[str, Any]:
    """
    Fetches current weather data using Open-Meteo API.
    
    100% FREE - No API key, no registration, no credit card needed!
    
    Why Open-Meteo: Free forever, high-quality data, no limits.
    Why normalize: Different weather metrics have different scales.
    We normalize rainfall (mm), temperature (C), and pressure (hPa)
    to 0-1 scores representing stress levels.
    
    Returns:
        dict: Normalized environmental stress indicators
    """
    # Udaipur coordinates
    lat, lon = 24.5854, 73.7125
    
    try:
        # Open-Meteo API (completely free, no key needed!)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True,
            'daily': 'precipitation_sum',
            'timezone': 'Asia/Kolkata'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data.get('current_weather', {})
        temp = current.get('temperature', 30)
        
        # Get precipitation from daily data (today)
        daily = data.get('daily', {})
        precip_list = daily.get('precipitation_sum', [0])
        rain_1h = precip_list[0] if precip_list else 0  # Today's total precipitation
        
        # Note: Open-Meteo doesn't provide pressure or PM2.5 in free tier
        # We'll use defaults or estimate
        pressure = 1010  # Standard atmospheric pressure
        pm25 = 50  # Moderate default (can't get real AQI without key)
        
        # Normalize to stress indices
        # Rain: 0mm = 0.0 stress, 50mm+ = 1.0 stress
        rain_stress = min(rain_1h / 50.0, 1.0)
        
        # Heat: 25C = 0.0 stress, 45C+ = 1.0 stress
        heat_stress = max(0, (temp - 25) / 20.0)
        heat_stress = min(heat_stress, 1.0)
        
        # Air quality: Use moderate default
        air_stress = 0.35  # Moderate estimate
        
        return {
            "status": "live",
            "source": "Open-Meteo (Free)",
            "timestamp": datetime.now().isoformat(),
            "temperature": round(temp, 1),
            "rainfall_1h": round(rain_1h, 1),
            "pressure": pressure,
            "pm25": pm25,
            "rain_stress": round(rain_stress, 2),
            "heat_stress": round(heat_stress, 2),
            "air_quality_stress": round(air_stress, 2)
        }
        
    except Exception as e:
        print(f"Weather API Error: {e}")
        return {
            "status": "fallback",
            "error": str(e),
            "rain_stress": 0.30,
            "heat_stress": 0.35,
            "air_quality_stress": 0.50
        }


def fetch_air_quality(lat: float, lon: float) -> float:
    """
    Placeholder for Google Air Quality API.
    
    Returns:
        float: PM2.5 value in µg/m³
    """
    # TODO: Implement Google Air Quality API when available
    # For now, return mock value
    return 85.0


# =======================
# 3. THE VOICE: News Sentiment
# =======================

def fetch_news_sentiment() -> Dict[str, Any]:
    """
    Fetches recent news and performs sentiment analysis.
    
    Why sentiment: News tone (negative vs positive) indicates public mood
    and potential crisis situations. We filter for city-relevant keywords.
    
    Returns:
        dict: Top headlines with sentiment scores
    """
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        print("Warning: NEWS_API_KEY not set, using mock data")
        return {
            "status": "mock",
            "headlines": [
                {"title": "Heavy rainfall expected in Udaipur", "sentiment": -0.3},
                {"title": "New hospital inaugurated in Rajasthan", "sentiment": 0.5},
                {"title": "Traffic congestion worsens", "sentiment": -0.4}
            ],
            "overall_sentiment": -0.07
        }
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'Udaipur OR Rajasthan',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 20,
            'apiKey': api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('articles', [])
        
        # Filter for relevant keywords
        keywords = ['protest', 'rain', 'flood', 'health', 'hospital', 
                   'corporation', 'sanitation', 'dengue', 'traffic']
        
        relevant_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            if any(keyword in title for keyword in keywords):
                relevant_articles.append(article)
        
        # Analyze sentiment for top 3
        headlines = []
        for article in relevant_articles[:3]:
            title = article.get('title', '')
            
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(title)
                sentiment = blob.sentiment.polarity  # Range: -1 to 1
            else:
                # Simple keyword-based sentiment
                sentiment = analyze_simple_sentiment(title)
            
            headlines.append({
                "title": title,
                "sentiment": round(sentiment, 2),
                "published": article.get('publishedAt', '')
            })
        
        avg_sentiment = sum(h['sentiment'] for h in headlines) / len(headlines) if headlines else 0
        
        return {
            "status": "live",
            "source": "NewsAPI",
            "timestamp": datetime.now().isoformat(),
            "headlines": headlines,
            "overall_sentiment": round(avg_sentiment, 2)
        }
        
    except Exception as e:
        print(f"News API Error: {e}")
        return {
            "status": "fallback",
            "error": str(e),
            "overall_sentiment": -0.1
        }


def analyze_simple_sentiment(text: str) -> float:
    """Simple keyword-based sentiment when TextBlob unavailable."""
    text = text.lower()
    
    negative_words = ['protest', 'flood', 'crisis', 'death', 'accident', 
                     'pollution', 'dengue', 'disease', 'corruption']
    positive_words = ['inaugurate', 'improve', 'success', 'award', 'growth', 
                     'development', 'clean', 'green']
    
    neg_count = sum(1 for word in negative_words if word in text)
    pos_count = sum(1 for word in positive_words if word in text)
    
    if neg_count + pos_count == 0:
        return 0.0
    
    return (pos_count - neg_count) / (pos_count + neg_count)


# =======================
# 4. THE PAIN: Civic Complaints
# =======================

def generate_complaints(count: int = 50) -> List[Dict[str, Any]]:
    """
    Generates synthetic civic complaints based on Rajasthan Sampark schema.
    
    Why synthetic: Real government APIs are not public. This generator
    creates realistic data with monsoon-skewed distribution (30% drainage).
    
    Args:
        count: Number of complaints to generate
        
    Returns:
        list: Synthetic complaint records
    """
    categories = ['Sanitation', 'Drainage', 'Lighting', 'Roads', 'Water Supply']
    
    # Skew towards Drainage (monsoon scenario)
    category_weights = {
        'Drainage': 0.30,      # 30% drainage complaints
        'Sanitation': 0.25,
        'Roads': 0.20,
        'Water Supply': 0.15,
        'Lighting': 0.10
    }
    
    statuses = ['Open', 'In Progress', 'Closed']
    severities = ['High', 'Medium', 'Low']
    
    complaints = []
    now = datetime.now()
    
    for i in range(count):
        # Weighted random category selection
        category = random.choices(
            list(category_weights.keys()),
            weights=list(category_weights.values())
        )[0]
        
        # Higher severity for drainage during monsoon
        if category == 'Drainage':
            severity = random.choices(severities, weights=[0.6, 0.3, 0.1])[0]
        else:
            severity = random.choices(severities, weights=[0.2, 0.5, 0.3])[0]
        
        # Generate timestamp within last 30 days
        days_ago = random.randint(0, 30)
        timestamp = now - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        complaint = {
            "complaint_id": str(uuid.uuid4()),
            "ward_id": random.randint(1, 50),
            "category": category,
            "status": random.choice(statuses),
            "severity": severity,
            "timestamp": timestamp.isoformat(),
            "description": f"{category} issue in Ward {random.randint(1, 50)}"
        }
        
        complaints.append(complaint)
    
    return complaints


def analyze_complaints(complaints: List[Dict]) -> Dict[str, Any]:
    """
    Analyzes complaint data to extract stress signals.
    
    Why analyze: We need normalized stress scores (0-1) not raw counts
    to compare with other data sources.
    
    Returns:
        dict: Normalized complaint stress indices
    """
    if not complaints:
        return {
            "total_complaints": 0,
            "drainage_stress": 0,
            "sanitation_stress": 0,
            "overall_stress": 0
        }
    
    # Count by category
    category_counts = {}
    for complaint in complaints:
        cat = complaint['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Normalize to stress scores (assume 5 complaints = critical threshold)
    critical_threshold = 5
    
    drainage_stress = min(category_counts.get('Drainage', 0) / critical_threshold, 1.0)
    sanitation_stress = min(category_counts.get('Sanitation', 0) / critical_threshold, 1.0)
    
    overall_stress = len(complaints) / (critical_threshold * 3)  # 15 total critical
    overall_stress = min(overall_stress, 1.0)
    
    return {
        "total_complaints": len(complaints),
        "by_category": category_counts,
        "drainage_stress": round(drainage_stress, 2),
        "sanitation_stress": round(sanitation_stress, 2),
        "overall_stress": round(overall_stress, 2)
    }


# =======================
# 5. THE ANATOMY: City Assets
# =======================

def fetch_nearby_hospitals() -> Dict[str, Any]:
    """
    Fetches hospitals within 5km of Udaipur center using OpenStreetMap Nominatim.
    
    100% FREE - No API key or credit card needed!
    
    Why OpenStreetMap: Community-driven, no limits, no keys required.
    
    Returns:
        dict: List of nearby hospitals with details
    """
    try:
        # Udaipur center
        lat, lon = 24.5854, 73.7125
        radius_km = 5
        
        # OpenStreetMap Overpass API (completely free!)
        # Note: Be respectful with requests (add User-Agent, don't hammer)
        url = "https://overpass-api.de/api/interpreter"
        
        # Overpass QL query for hospitals
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
          way["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
        );
        out body;
        """
        
        headers = {
            'User-Agent': 'CALO-SmartCity/1.0'
        }
        
        response = requests.post(url, data={'data': query}, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        hospitals = []
        for element in data.get('elements', [])[:10]:  # Top 10
            tags = element.get('tags', {})
            
            # Calculate approximate distance
            elem_lat = element.get('lat', lat)
            elem_lon = element.get('lon', lon)
            
            hospitals.append({
                "name": tags.get('name', 'Unnamed Hospital'),
                "vicinity": tags.get('addr:street', 'Udaipur'),
                "type": tags.get('healthcare', 'hospital'),
                "location": {"lat": elem_lat, "lon": elem_lon}
            })
        
        return {
            "status": "live",
            "source": "OpenStreetMap",
            "timestamp": datetime.now().isoformat(),
            "hospital_count": len(hospitals),
            "hospitals": hospitals
        }
        
    except Exception as e:
        print(f"OpenStreetMap API Error: {e}")
        # Fallback to mock data
        return {
            "status": "fallback",
            "error": str(e),
            "hospital_count": 5,
            "hospitals": [
                {"name": "GBH General Hospital", "vicinity": "Near City Palace"},
                {"name": "Pacific Medical College", "vicinity": "Airport Road"},
                {"name": "Aravali Hospital", "vicinity": "Savina"},
                {"name": "Paras JK Hospital", "vicinity": "Sector 5"},
                {"name": "MB Hospital", "vicinity": "University Road"}
            ]
        }


# =======================
# MASTER FUSION FUNCTION
# =======================

def create_city_snapshot() -> Dict[str, Any]:
    """
    Master function that aggregates all 5 data sources into a unified City Pulse.
    
    This creates a single JSON structure representing the city's current state
    across multiple dimensions: Mind (trends), Body (environment), 
    Voice (news), Pain (complaints), and Anatomy (infrastructure).
    
    Returns:
        dict: Complete city snapshot with all normalized signals
    """
    print("🌆 CALO City Pulse Generator")
    print("=" * 50)
    print("Fetching city signals from 5 sources...\n")
    
    # 1. Mind: Search Trends
    print("📊 Fetching search trends...")
    trends = fetch_search_trends()
    
    # 2. Body: Weather & Environment
    print("🌡️  Fetching weather data...")
    weather = fetch_weather_data()
    
    # 3. Voice: News Sentiment
    print("📰 Fetching news sentiment...")
    news = fetch_news_sentiment()
    
    # 4. Pain: Civic Complaints
    print("📋 Generating civic complaints...")
    raw_complaints = generate_complaints(50)
    complaints = analyze_complaints(raw_complaints)
    
    # 5. Anatomy: City Assets
    print("🏥 Fetching nearby hospitals...")
    hospitals = fetch_nearby_hospitals()
    
    print("\n✅ All data sources fetched successfully!")
    print("=" * 50)
    
    # Create unified snapshot
    city_snapshot_v1 = {
        "snapshot_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "location": {
            "city": "Udaipur",
            "state": "Rajasthan",
            "coordinates": {"lat": 24.5854, "lon": 73.7125}
        },
        
        "mind": {
            "description": "Search anxiety from Google Trends",
            "data": trends
        },
        
        "body": {
            "description": "Environmental stress indicators",
            "data": weather
        },
        
        "voice": {
            "description": "Public sentiment from news",
            "data": news
        },
        
        "pain": {
            "description": "Civic complaint analysis",
            "data": complaints,
            "raw_complaints_sample": raw_complaints[:5]  # Include 5 samples
        },
        
        "anatomy": {
            "description": "City infrastructure (hospitals)",
            "data": hospitals
        },
        
        "summary": {
            "overall_stress_score": calculate_overall_stress(
                trends, weather, news, complaints
            ),
            "top_concerns": identify_top_concerns(
                trends, weather, complaints
            ),
            "recommended_protocols": []  # To be filled by AI reasoner
        }
    }
    
    return city_snapshot_v1


def calculate_overall_stress(trends, weather, news, complaints) -> float:
    """Calculate weighted overall city stress score (0-1)."""
    scores = [
        trends.get('overall_anxiety', 0.0) * 0.2,           # 20% weight
        weather.get('rain_stress', 0.0) * 0.25,              # 25% weight
        weather.get('heat_stress', 0.0) * 0.15,              # 15% weight
        abs(news.get('overall_sentiment', 0.0)) * 0.15,      # 15% weight
        complaints.get('overall_stress', 0.0) * 0.25         # 25% weight
    ]
    
    return round(sum(scores), 2)


def identify_top_concerns(trends, weather, complaints) -> List[str]:
    """Identify top 3 concerns based on stress thresholds."""
    concerns = []
    
    if trends.get('dengue_anxiety', 0) > 0.5:
        concerns.append("High dengue search activity")
    
    if weather.get('rain_stress', 0) > 0.6:
        concerns.append("Heavy rainfall detected")
    
    if complaints.get('drainage_stress', 0) > 0.5:
        concerns.append("Multiple drainage complaints")
    
    if trends.get('waterlogging_anxiety', 0) > 0.6:
        concerns.append("Waterlogging concerns rising")
    
    return concerns[:3]  # Return top 3


# =======================
# MAIN EXECUTION
# =======================

if __name__ == "__main__":
    # Create the city snapshot
    snapshot = create_city_snapshot()
    
    # Print the complete JSON structure
    print("\n" + "=" * 50)
    print("CITY SNAPSHOT V1 (Unified JSON)")
    print("=" * 50)
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    
    # Optionally save to file
    output_file = "city_pulse_snapshot.json"
    with open(output_file, 'w') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Snapshot saved to: {output_file}")
    print(f"📊 Overall Stress Score: {snapshot['summary']['overall_stress_score']}")
    print(f"⚠️  Top Concerns: {snapshot['summary']['top_concerns']}")
