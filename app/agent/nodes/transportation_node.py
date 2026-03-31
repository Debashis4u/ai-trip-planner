import json
import os
import re
import time
from app.agent.groq_client import get_groq_client, create_chat_completion
import os
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def transportation_node(state: dict):
    destination = state.get("destination")
    budget = state.get("budget")
    currency = state.get("currency") or "USD"
    duration = state.get("duration")
    start_date = state.get("start_date")
    end_date = state.get("end_date")
    preferences = state.get("preferences", [])

    if not destination:
        return {
            **state,
            "transportation": "No destination specified"
        }

    date_info = ""
    if start_date and end_date:
        date_info = f" from {start_date} to {end_date}"
    elif start_date:
        date_info = f" starting {start_date}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = get_groq_client()

            
            prefs_text = ", ".join(preferences) if preferences else "general"
            
            prompt = f"""
            Suggest transportation options for a {duration}-day trip to {destination}{date_info}.
            Budget: {budget} {currency} total
            Preferences: {prefs_text}
            
            Consider getting to/from the destination, local transportation, and any travel within the trip.
            Check for seasonal availability or booking considerations for the dates.
            Suggest cost-effective options that fit the budget and preferences.
            
            Provide detailed transportation recommendations with costs and options.
            """

            response = create_chat_completion(client, 
                                messages=[
                    {"role": "system", "content": "You are a transportation expert. Provide detailed transportation recommendations."},
                    {"role": "user", "content": prompt}
                ],
                                                temperature=0.8,
                max_tokens=400
            )

            result_text = response.choices[0].message.content.strip()
            
            return {
                **state,
                "transportation": result_text
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"❌ Rate limit hit in transportation, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Transportation Error: {error_msg}")
                return {
                    **state,
                    "transportation": f"Flight to {destination}, local taxis/buses (~100-200 {currency} total)",
                    "errors": state.get("errors", []) + [f"Transportation suggestion failed: {error_msg}"]
                }