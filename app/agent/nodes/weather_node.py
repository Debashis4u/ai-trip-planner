# app/agent/nodes/weather_node.py

from app.agent.tools.weather_tool import get_weather
from datetime import datetime

def weather_node(state: dict):
    destination = state.get("destination")
    start_date = state.get("start_date")

    weather = get_weather(destination, start_date)

    return {
        **state,
        "weather": weather
    }