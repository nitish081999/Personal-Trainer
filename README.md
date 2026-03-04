# Personal Trainer AI Orchestrator

This repository contains the full stack application for the Personal Trainer AI System.

## Architecture

![Architecture](https://via.placeholder.com/800x400?text=Architecture+Diagram)

* **Frontend:** Next.js application (React, TailwindCSS)
* **Backend:** FastAPI (Python) orchestrating mining, tests, LLMs.
* **Database:** SQLite (mocked for development), switchable to Postgres (Supabase).

## Components

1. **LLM Router:** Intelligent fallback mechanism between Groq, Gemini, and Mistral based on API limits and rate tracking.
2. **Search Router:** Multi-API search engine utilizing Tavily, Serper, and DuckDuckGo with synthetic fallback.
3. **Mining Engine:** Background worker that generates search queries, extracts raw content, structures JSON MCQs, and deduplicates.
4. **Adaptive Learning Engine:** Calculates user weakness scores over time (weighting recent attempts) to generate revision tests.

## Running the Application

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `uvicorn main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

Navigate to `http://localhost:3000` for the frontend and `http://localhost:8000/docs` for the API OpenAPI spec.
