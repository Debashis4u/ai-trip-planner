# app/main.py

from dotenv import load_dotenv
load_dotenv()  # Must happen before importing components that read env vars

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.agent.graph import build_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()   # ✅ VERY IMPORTANT

static_dir = Path(__file__).parent / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

graph = build_graph()

class TripRequest(BaseModel):
    message: str
    tripDate: str | None = None  # Format: YYYY-MM-DD

@app.get("/")
async def root():
    return FileResponse(static_dir / "index.html")

@app.get("/api")
async def api_root():
    return {"message": "Trip Planner API", "endpoints": ["/plan-trip (POST)", "/health (GET)"]}

@app.post("/plan-trip")
async def plan_trip(request: TripRequest):
    from datetime import datetime, timedelta
    
    logger.info(f"Planning trip for: {request.message}")
    context = {
        "user_input": request.message
    }
    if request.tripDate:
        context["start_date"] = request.tripDate
        logger.info(f"Trip date: {request.tripDate}")
        # Calculate tentative end_date (will be updated after duration is parsed)
        try:
            start = datetime.strptime(request.tripDate, "%Y-%m-%d")
            end = start + timedelta(days=2)  # Default 3-day trip
            context["end_date"] = end.strftime("%Y-%m-%d")
        except ValueError:
            pass
    result = graph.invoke(context)
    logger.info(f"Trip plan result: {result}")
    return result

@app.get("/health")
async def health_check():
    return {"status": "healthy"}