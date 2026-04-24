# AI Visibility Intelligence API
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)]()

A RESTful Flask API with a multi-agent AI backend that discovers, scores and tracks high-value competitive queries for AI-generated answer engines.

## Tech Stack
* **Framework:** Python 3.12, Flask 3.0.3
* **Database:** PostgreSQL 16, SQLAlchemy 2.0, Alembic
* **Validation & Types:** Pydantic v2, MyPy
* **AI Provider:** Anthropic (Claude 4.6 Sonnet)
* **Background Processing:** Celery + Redis
* **Telemetry:** `structlog` (Distributed Correlation IDs)
* **Infrastructure:** Multi-stage Docker, Docker Compose

---

## 🧠 Architecture & Agent Design

The application utilizes a distributed, asynchronous architecture. When a user triggers an analysis, the Flask API immediately returns a `202 Accepted` and offloads the heavy LLM workflow to a Celery worker via Redis. 

The background task is executed using a **Multi-Agent Strategy Pattern**:

1. **Agent 1: Query Discovery Agent**
   * Analyzes the business profile and competitors to generate realistic, long-tail conversational queries that users ask AI engines.
2. **Agent 2: Opportunity Scoring Agent**
   * Fetches search volume and difficulty metrics (via DataForSEO).
   * Calculates an overall opportunity score to prioritize queries based on competitive gaps.
3. **Agent 3: Content Recommendation Agent**
   * Selects the highest-scoring queries and generates actionable content recommendations (e.g Comparison Guides, FAQs) designed specifically to increase AI citation probability.

---

## 📊 Opportunity Score Formula

The Opportunity Score (0.0 to 1.0) determines the strategic value of a discovered query. It balances semantic relevance, SEO difficulty and AI search volume.

**Formula:**
`Score = (Base Relevance * 0.4) + (Volume Factor * 0.3) + (Difficulty Factor * 0.3)`

**Worked Example:**
* **Base Relevance:** 0.8 (Determined by LLM based on competitor gap)
* **Search Volume:** 1,200 (Normalized against a ceiling of 10,000 -> 0.12)
* **Keyword Difficulty:** 30 (Inverted -> `(100 - 30) / 100` = 0.70)
* **Calculation:** `(0.8 * 0.4) + (0.12 * 0.3) + (0.70 * 0.3)` = `0.32 + 0.036 + 0.21` = **0.566**

---

## ⚖️ Engineering Tradeoffs & Decisions

* **Mocked Data vs. Real API:** The application includes a fully functional DataForSEO v3 integration. The app defaults to a `MockSEOProvider` for reliable testing, but the real API can be activated via the `USE_REAL_SEO_DATA=true` feature flag.
* **Async Celery Execution:** LLM chains taking 30-100 seconds will cause HTTP timeouts in production. We shifted the pipeline to Celery to return immediate `202` responses, adhering to RESTful standards for long-running operations.
* **Distributed Tracing:** Standard logging breaks down in async environments. We implemented `structlog` to inject a `Correlation ID` at the Flask edge, which propagates through Redis to the Celery worker for seamless request tracing.

---

## 🚀 Setup Instructions

### 1. Environment Variables
Copy the example environment file and insert your API keys:
```bash
cp .env.example .env
```
Ensure `ANTHROPIC_API_KEY` is populated.

### 2. Docker Path (Recommended / Cold-Start)
The entire application (API, Worker, DB, Redis) is containerized. 
```bash
docker compose up --build
```
*The `entrypoint.sh` script will automatically apply database migrations before starting the API.*

### 3. Local Development Path
If you prefer running the app locally outside of Docker:
```bash
# 1. Start backing services
docker compose up -d db redis

# 2. Install dependencies
python -m venv env
source env/bin/activate  # Windows: .\env\Scripts\activate
pip install -r requirements.txt

# 3. Start the Flask API
flask run

# 4. Start the Celery Worker (In a separate terminal)
celery -A app.celery_app.celery worker --loglevel=info --pool=solo
```

---

## 📖 API Reference

### 1. Create a Business Profile
`POST /api/v1/profiles`
```json
{
    "name": "Bitvizo",
    "domain": "bitvizo.io",
    "industry": "Algorithmic Cryptocurrency Trading",
    "description": "Bitvizo is an advanced trading platform for creating and backtesting automated bots.",
    "competitors": ["3commas", "Cryptohopper"]
}
```
**Response:** `201 Created` - Returns `{ "profile_uuid": "..." }`

### 2. Trigger AI Analysis
`POST /api/v1/profiles/<PROFILE_UUID>/analyze`
*(Rate Limited: 2 per minute)*
**Response:** `202 Accepted` - Returns `{ "run_uuid": "...", "status": "pending" }`

### 3. Retrieve Results
`GET /api/v1/profiles/<PROFILE_UUID>/queries`
`GET /api/v1/profiles/<PROFILE_UUID>/recommendations`
**Response:** `200 OK` - Returns lists of generated AI queries and content strategies.

---

## 🧪 Testing & Code Quality

Run the test suite (uses mocked database and LLM endpoints):
```bash
pytest tests/ -v
```

Lint and format code:
```bash
ruff check .
black .
mypy app/
```