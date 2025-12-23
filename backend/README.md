# CALO Backend

AI reasoning layer for the CALO system.

## Setup
1. `pip install -r requirements.txt`
2. `cp .env.example .env` (and add API key)
3. `uvicorn src.app:app --reload`

## Real Data Mode
To enable real-time data fetching (Weather API, News RSS):
1. Open `.env`
2. Set `USE_REAL_DATA=True`

Note: This will attempt to fetch data from Open-Meteo and Times of India RSS. If it fails, the system automatically falls back to mock data in `src/data/`.
