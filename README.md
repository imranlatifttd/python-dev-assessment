# AI Visibility Intelligence API

A RESTful Flask API with a multi-agent backend that discovers, scores and tracks high-value competitive queries for AI-generated answers (Claude).

## Tech Stack
* **Framework:** Python 3.12, Flask 3.0.3
* **Database:** PostgreSQL 16, SQLAlchemy 2.0, Alembic
* **Validation:** Pydantic v2
* **AI Provider:** Anthropic (Claude Sonnet 3.5)
* **Background Processing:** Celery + Redis

## Project Goals
1. Register business profiles and trigger a multi-agent AI pipeline.
2. Discover high-value AI queries using competitive intelligence.
3. Score queries based on search volume, difficulty, and visibility gaps.
4. Generate actionable content recommendations to improve AI visibility.

Full setup instructions, architecture decisions and the opportunity score formula will be documented here

## Local Development Setup

### 1. Environment Variables
Copy the example environment file:
```powershell
Copy-Item .env.example -Destination .env
```
*(You will need to add your Anthropic API key to the `.env` file before running the pipeline).*

### 2. Database Setup
We use Docker to run a local PostgreSQL 16 database. Ensure Docker Desktop is running.

**Start the database locally:**
```powershell
docker compose up -d db
```

**Verify the database container is running and healthy:**
```powershell
docker compose ps
```

The database is accessible locally at `postgresql+psycopg2://postgres:postgres@localhost:5432/ai_visibility`.

**Verify the database connection via Python:**
Run the following in python shell to ensure your environment can connect to the database:
```python
import psycopg2
conn = psycopg2.connect("dbname=ai_visibility user=postgres password=postgres host=localhost port=5432")
print("Connected successfully!" if conn else "Connection failed.")
conn.close()
```