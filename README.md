# 🧠 CALO (City as a Living Organism)

## 📁 Complete Project Structure (Single Repo)

```
calo/
│
├── backend/                         # AI + Logic (Person 1)
│   ├── src/
│   │   ├── app.py                   # Main API entry (/analyze)
│   │   │
│   │   ├── services/
│   │   │   ├── data_loader.py       # Load CSV, weather, trends, news
│   │   │   ├── signal_builder.py    # Convert raw data → city signals
│   │   │   ├── ai_reasoner.py       # Gemini reasoning layer
│   │   │   └── insight_formatter.py # Format insights for UI
│   │   │
│   │   ├── data/
│   │   │   ├── complaints.csv       # Sample public data
│   │   │   ├── news.json
│   │   │   └── trends.json
│   │   │
│   │   ├── prompts/
│   │   │   └── city_reasoning.txt   # Gemini prompt template
│   │   │
│   │   └── config/
│   │       ├── settings.py          # Thresholds, city name
│   │       └── constants.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                        # UI + Storytelling (Person 2)
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── CityStatus.js        # City health summary
│   │   │   ├── Explanation.js       # Why CALO thinks this
│   │   │   └── Prediction.js        # What might happen next
│   │   │
│   │   ├── scripts/
│   │   │   └── main.js              # API call + render logic
│   │   │
│   │   ├── styles/
│   │   │   └── main.css
│   │   │
│   │   └── config/
│   │       └── api.js               # Backend API URL
│   │
│   ├── mock/
│   │   └── sample_response.json
│   │
│   └── README.md
│
├── contract/
│   └── response_schema.json         # Backend–Frontend API contract
│
├── .gitignore
└── README.md                        # Main project description
```

---

# 🛠️ Tech Stack (Simple & Strong)

## 🔹 Backend (AI + Data)

* **Language:** Python
* **Framework:** Flask or FastAPI
* **AI:** Gemini API (reasoning + explanation)
* **Data:** CSV + public APIs (weather, trends, news)
* **Purpose:** Convert city data → signals → insights

---

## 🔹 Frontend (UI)

* **Language:** HTML, CSS, JavaScript
* **Framework:** None (or optional React later)
* **Purpose:** Display city health story clearly
* **Style:** Minimal, narrative, readable

---

## 🔹 AI Usage

* **Gemini API**

  * Signal correlation
  * Plain-language explanations
  * Near-future risk reasoning
* **No ML training**
* **No IoT**

---

## 🔹 Dev & Deployment

* **Version Control:** Git + GitHub
* **Secrets:** `.env` (ignored)
* **Deployment (optional):**

  * Backend → Google Cloud Run / Render
  * Frontend → Vercel / Netlify

---

# 🎯 Why This Stack Works

* Student-friendly
* Fast to build
* Easy to explain to judges
* Looks professional
* Scales later without refactor

---

## 🧠 One-Line Summary

> CALO is a clean AI-powered city intelligence system built with Python, Gemini, and a simple web UI — no sensors, no hardware, just reasoning.
