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