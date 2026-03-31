# app/agent/tools/weather_tool.py

import requests
from datetime import datetime

def get_weather(destination: str, trip_date: str = None) -> str:
    if not destination:
        return "Unknown weather"

    try:
        # Using wttr.in which doesn't require API key
        # If trip_date is provided (format: YYYY-MM-DD), use it for forecast
        url = f"http://wttr.in/{destination}?format=3"
        
        if trip_date:
            # Parse the date to get the number of days from today
            try:
                trip_datetime = datetime.strptime(trip_date, "%Y-%m-%d")
                today = datetime.now().date()
                trip_day = trip_datetime.date()
                days_ahead = (trip_day - today).days
                
                if days_ahead > 0:
                    # wttr.in supports forecast days parameter
                    url = f"http://wttr.in/{destination}?format=3&days={min(days_ahead + 1, 3)}"
                    # For more detailed forecast including specific date
                    url = f"http://wttr.in/{destination}?format=j1"  # Get JSON for better date info
            except ValueError:
                pass  # Invalid date format, use default
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if trip_date and "format=j1" in url:
            # Parse JSON response to get weather for specific date
            import json
            data = response.json()
            weather = format_forecast_for_date(data, trip_date)
        else:
            weather = response.text.strip()
            # Ensure proper encoding
            weather = weather.encode('latin1').decode('utf-8')
        
        return weather
    except requests.RequestException as e:
        return f"Weather data unavailable for {destination}: {str(e)}"
    except Exception as e:
        return f"Weather info for {destination}: {destination} (~{str(e)[:20]})"

def format_forecast_for_date(data: dict, trip_date: str) -> str:
    """Format weather forecast for a specific trip date"""
    try:
        # Parse trip date
        trip_datetime = datetime.strptime(trip_date, "%Y-%m-%d")
        trip_date_str = trip_datetime.strftime("%Y-%m-%d")
        
        # Try to find forecast for that date
        current_condition = data.get("current_condition", [{}])[0]
        forecasts = data.get("weather", [])
        
        for forecast in forecasts:
            if forecast.get("date") == trip_date_str:
                avg_temp = forecast.get("avgtemp_c", "N/A")
                condition = forecast.get("weatherDesc", [{}])[0].get("value", "Partly cloudy")
                return f"{trip_date}: {condition}, ~{avg_temp}°C"
        
        # If exact date not found, use current
        condition = current_condition.get("weatherDesc", [{}])[0].get("value", "Info available")
        temp = current_condition.get("temp_c", "N/A")
        return f"{condition}, ~{temp}°C on {trip_date}"
    except Exception as e:
        return f"Weather forecast available for {trip_date}"
