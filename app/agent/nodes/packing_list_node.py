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

def packing_list_node(state: dict):
    destination = state.get("destination")
    duration = state.get("duration")
    weather = state.get("weather")
    preferences = state.get("preferences", [])
    plan = state.get("plan", [])

    if not destination:
        return {
            **state,
            "packing_list": ["Basic travel essentials"]
        }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = get_groq_client()

            prefs_text = ", ".join(preferences) if preferences else "general"
            plan_text = "\n".join(plan[:3]) if plan else "general activities"  # Use first few days
            
            prompt = f"""
            Create a packing list for a {duration}-day trip to {destination}.
            Weather: {weather}
            Activities: {plan_text}
            Preferences: {prefs_text}
            
            Include essentials, weather-appropriate clothing, activity-specific items, and toiletries.
            Consider the season and activities planned.
            
            Respond with ONLY a JSON object like: {{"packing_list": ["item1", "item2", ...]}}
            """

            response = create_chat_completion(client, 
                                messages=[
                    {"role": "system", "content": "You are a packing expert. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                                                temperature=0.6,
                max_tokens=400
            )

            result_text = response.choices[0].message.content.strip()

            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()

            data = json.loads(result_text)
            packing_list = data.get("packing_list", [])
            
            return {
                **state,
                "packing_list": packing_list
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"❌ Rate limit hit in packing_list, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Packing List Error: {error_msg}")
                return {
                    **state,
                    "packing_list": [
                        "Passport/ID",
                        "Clothing for weather",
                        "Toiletries",
                        "Chargers",
                        "Comfortable shoes"
                    ],
                    "errors": state.get("errors", []) + [f"Packing list generation failed: {error_msg}"]
                }