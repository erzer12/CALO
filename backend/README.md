# CALO - City as a Living Organism 🌆

**AI-Powered Urban Intelligence System for Smart Cities**

CALO is a production-ready backend system that analyzes real-time city data from multiple sources to detect risks, match operational protocols, and provide actionable insights for municipal decision-making.

---

## 🎯 What Does CALO Do?

CALO acts as a "digital brain" for cities, continuously monitoring:
- 🌡️ **Weather patterns** (rainfall, temperature, air quality)
- 📰 **News sentiment** (public mood and events)
- 📊 **Search trends** (health concerns, traffic, issues)
- 📋 **Civic complaints** (sanitation, drainage, infrastructure)
- 🏥 **City infrastructure** (hospitals, resources)

It then:
1. **Detects risks** using rule-based logic (vector-borne disease, floods, heatwaves)
2. **Matches protocols** with actionable recommendations
3. **Provides dual views**: Simple status for citizens, detailed diagnostics for engineers

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Data Loader  │ -> │ Logic Engine │ -> │ AI Reasoner  │ │
│  │              │    │              │    │              │ │
│  │ • Weather    │    │ • Normalize  │    │ • Protocols  │ │
│  │ • News       │    │ • Evaluate   │    │ • Reasoning  │ │
│  │ • Trends     │    │ • Detect     │    │ • Formatting │ │
│  │ • Complaints │    │   Risks      │    │              │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
│                  ↓ JSON Response ↓                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  {                                                   │  │
│  │    "status": "Warning",                             │  │
│  │    "citizen_view": { "status_headline": "..." },    │  │
│  │    "engineer_view": {                               │  │
│  │      "detected_risks": [...],                       │  │
│  │      "recommended_actions": [...]                   │  │
│  │    }                                                 │  │
│  │  }                                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
CALO/
├── backend/
│   ├── src/
│   │   ├── app.py                          # FastAPI main application
│   │   ├── config/
│   │   │   └── settings.py                 # Environment config & thresholds
│   │   ├── models/
│   │   │   └── schemas.py                  # Pydantic models for validation
│   │   ├── services/
│   │   │   ├── data_loader.py              # Multi-source data aggregation
│   │   │   ├── city_pulse_generator.py     # 5-source enhanced pipeline
│   │   │   ├── logic_engine.py             # Risk detection algorithms
│   │   │   ├── ai_reasoner.py              # AI reasoning with Gemini
│   │   │   └── insight_formatter.py        # Response formatting
│   │   └── data/
│   │       ├── protocols.json              # Operational protocols (Dengue, Flood, etc.)
│   │       └── mock/                       # Mock data for development
│   ├── tests/                              # Pytest test suite
│   │   ├── conftest.py                     # Test fixtures
│   │   ├── test_logic_engine.py            # Logic tests
│   │   └── test_api.py                     # API integration tests
│   ├── requirements.txt                    # Python dependencies
│   ├── .env.example                        # Environment variables template
│   └── README.md                           # This file
│
├── frontend/
│   └── public/                             # HTML/CSS/JS frontend
│
└── contract/
    └── response_schema.json                # API contract definition
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- pip package manager
- (Optional) API keys for enhanced data sources

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# At minimum, set GEMINI_API_KEY if you want AI reasoning
```

### 3. Configuration

Edit `.env` file:

```bash
# Required
CITY_NAME=Udaipur
ENVIRONMENT=development

# Optional: AI Integration
GEMINI_API_KEY=your-key-here

# Optional: Enhanced Data Sources
OPENWEATHER_API_KEY=your-key
NEWS_API_KEY=your-key
GOOGLE_PLACES_API_KEY=your-key

# Toggle real vs mock data
USE_REAL_DATA=True
```

### 4. Run the Server

```bash
# Start the backend
uvicorn src.app:app --reload

# Server runs on http://localhost:8000
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/

# Run analysis
curl http://localhost:8000/api/v1/analyze
```

---

## 📡 API Endpoints

### GET `/`
**Health Check** - Returns service status

**Response:**
```json
{
  "status": "CALO Backend Operational",
  "services": {
    "gemini_api": "connected",
    "data_loader": "operational",
    "logic_engine": "operational"
  },
  "version": "0.2"
}
```

---

### GET `/api/v1/analyze`
**City Analysis** - Main intelligence endpoint

**Response Schema:**
```json
{
  "status": "Healthy|Warning|Critical",
  "summary": "Brief status headline",
  "details": ["Risk details..."],
  "future": "Recommendations...",
  
  "citizen_view": {
    "status_headline": "Simple message for citizens",
    "visual_theme": "Normal|Caution|Critical"
  },
  
  "engineer_view": {
    "confidence_score": 0.85,
    "detected_risks": ["Vector-Borne Disease Cluster"],
    "raw_signals": {
      "weather": 0.75,
      "complaints": 0.4,
      "trends": 0.9
    },
    "logic_trace": "Step-by-step analysis...",
    "recommended_actions": [
      "Deploy fogging trucks to zones A/B",
      "Launch SMS awareness campaign"
    ]
  }
}
```

---

## 🔧 How It Works

### Data Flow

1. **Data Collection** (`data_loader.py`)
   - Fetches real-time data from APIs (weather, news)
   - Loads complaint/trend data
   - Falls back to mock data if APIs unavailable

2. **Signal Normalization** (`logic_engine.py`)
   - Converts raw data to 0-1 stress scores
   - Example: Rainfall 25mm → 0.5 stress (50mm = critical)
   - Configurable thresholds via `settings.py`

3. **Risk Evaluation** (`logic_engine.py`)
   - Applies rule-based logic to detect scenarios
   - **BIO_RISK**: High rainfall + sanitation issues + health trends
   - **FLOOD_RISK**: Extreme rain + drainage complaints
   - **HEAT_RISK**: High temperature sustained

4. **Protocol Matching** (`ai_reasoner.py`)
   - Matches detected risks to operational protocols
   - Protocols defined in `data/protocols.json`
   - Each protocol has specific triggers and actions

5. **AI Reasoning** (`ai_reasoner.py`)
   - Uses Gemini AI to generate natural language insights
   - Falls back to rule-based analysis if AI unavailable
   - Combines all data for comprehensive response

6. **Response Formatting** (`insight_formatter.py`)
   - Transforms AI output to match API contract
   - Ensures consistency for frontend

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_logic_engine.py -v
```

**Test Coverage:**
- ✅ Signal normalization
- ✅ Risk detection algorithms
- ✅ API endpoint responses
- ✅ Error handling
- ✅ CORS configuration

---

## 🎛️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | `development` or `production` | `development` |
| `LOG_LEVEL` | Logging level | `DEBUG` |
| `USE_REAL_DATA` | Enable live API calls | `False` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |
| `GEMINI_API_KEY` | Google Gemini API key | - |

### Risk Thresholds

Customize in `.env` or `settings.py`:

```python
RAINFALL_CRITICAL_MM = 50          # Rainfall threshold
TEMP_NEUTRAL_C = 25                # Comfortable temperature
TEMP_MAX_C = 45                    # Critical heat
COMPLAINTS_CRITICAL = 5            # Alert threshold
DISEASE_RISK_THRESHOLD = 0.4       # Bio risk sensitivity
FLOOD_RISK_THRESHOLD = 0.5         # Flood detection
HEAT_RISK_THRESHOLD = 0.6          # Heatwave detection
```

---

## 📊 Enhanced Data Sources

The `city_pulse_generator.py` module provides 5 additional data sources:

1. **Google Trends** (pytrends) - Search anxiety indices
2. **OpenWeatherMap** - Detailed weather + air quality
3. **NewsAPI** - News sentiment analysis
4. **Synthetic Complaints** - Realistic civic complaint generator
5. **Google Places** - Hospital/infrastructure mapping

**Run standalone:**
```bash
python src/services/city_pulse_generator.py
```

---

## 🔒 Security Features

- ✅ **Environment-based CORS** (development vs production)
- ✅ **Input validation** via Pydantic models
- ✅ **Error sanitization** (no stack traces in production)
- ✅ **Structured logging** for security monitoring
- ✅ **API key management** via environment variables

**Production Checklist:**
- Set `ENVIRONMENT=production` in `.env`
- Configure `ALLOWED_ORIGINS` to your domain
- Use HTTPS reverse proxy (nginx)
- Enable rate limiting (SlowAPI included)
- Monitor logs for anomalies

---

## 📈 Extending CALO

### Adding a New Risk Type

1. **Define detection logic** in `logic_engine.py`:
```python
def _detect_traffic_jam(self, signals: Dict) -> Optional[Dict]:
    if signals.get('traffic_anxiety') > 0.6:
        return {
            "id": "TRAFFIC_RISK",
            "name": "Severe Traffic Congestion",
            # ...
        }
```

2. **Create protocol** in `data/protocols.json`:
```json
{
  "id": "TRAFFIC_1A",
  "name": "Traffic Management Protocol",
  "matches_risk_ids": ["TRAFFIC_RISK"],
  "actions": ["Deploy traffic marshals", "..."]
}
```

3. **Add to evaluation** in `evaluate_risk()` method

### Adding a New Data Source

1. Create fetcher in `data_loader.py`
2. Add normalization in `logic_engine.py`
3. Update `settings.py` with API keys
4. Add fallback data in `src/data/mock/`

---

## 🐛 Troubleshooting

### Gemini API Not Working
- **Issue**: 404 model errors
- **Solution**: System automatically uses rule-based fallback with real data
- **Note**: Google's SDK is in transition - see [Issue #1]

### CORS Errors
- **Issue**: Frontend can't connect
- **Solution**: Add frontend URL to `ALLOWED_ORIGINS` in `.env`
- **Development**: Set `ENVIRONMENT=development` for localhost wildcard

### No Data Returning
- **Issue**: APIs failing
- **Solution**: Set `USE_REAL_DATA=False` for mock data
- **Check**: Review logs for specific API errors

---

## 📝 Development Notes

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking (if using mypy)
mypy src/
```

### Adding Dependencies

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Guidelines:**
- Write tests for new features
- Update README for API changes
- Follow existing code style
- Add docstrings to functions

---

## 📄 License

This project is part of a Smart City initiative. See LICENSE file for details.

---

## 🙏 Acknowledgments

- **Tech Stack**: FastAPI, Pydantic, Gemini AI
- **Data Sources**: Open-Meteo, NewsAPI, Google Trends
- **Inspiration**: Smart City frameworks and urban informatics

---

## 📞 Support

For issues and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review logs: `tail -f backend.log`
- Open an issue with error logs and environment details

---

**Built with ❤️ for Smarter Cities**
