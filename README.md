# Trip Planner

A production-ready AI-powered trip planning application using FastAPI, LangGraph, Groq LLM, and a React-based web UI.

## Features

- Parse user trip requests using LLM
- Fetch real-time weather data
- Generate detailed trip plans
- React front end served directly by FastAPI
- Error handling and fallbacks

## Setup

1. Install uv (if not already installed):
   ```bash
   pip install uv
   ```

2. Clone or navigate to the project directory.

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. Run the application:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

6. Open the app in your browser:
   ```
   http://127.0.0.1:8000
   ```

## Front End

The browser UI is a lightweight React app served from `app/static` by FastAPI.

- `GET /` serves the React UI
- `POST /plan-trip` is used by the UI to generate plans
- `GET /api` returns a simple API summary
- `GET /health` returns health status

This setup does not require a separate Node build step.

If you later want a separate Vite-based React workspace, upgrade Node.js to 20+ first. The current machine is using Node 15, which is too old for current Vite tooling.

## API Usage

Send a POST request to `/plan-trip` with JSON:
```json
{
  "message": "Plan a 2 day Goa trip under 15000"
}
```

Response includes parsed details, weather, and generated plan.

## Architecture

- `app/main.py`: FastAPI app, API routes, and React static file serving
- `app/static`: React UI assets
- `parse_node`: Extracts destination, budget, duration from user input
- `weather_node`: Fetches weather using wttr.in API
- `plan_node`: Generates itinerary using Groq LLM with fallback