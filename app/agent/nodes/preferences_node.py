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

def preferences_node(state: dict):
    user_input = state.get("user_input", "")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = get_groq_client()
            prompt = f"""
            Extract user preferences and interests from this trip request: "{user_input}"
            
            Look for mentions of activities, interests, or preferences like:
            - Adventure/sports
            - Culture/history
            - Food/cuisine
            - Relaxation/beach
            - Shopping
            - Nature/outdoors
            - Nightlife
            - Family-friendly
            - Budget-conscious
            - Luxury
            
            Respond with ONLY a JSON object like: {{"preferences": ["preference1", "preference2", ...]}}
            If no specific preferences mentioned, return an empty array.
            """

            response = create_chat_completion(client, 
                                messages=[
                    {"role": "system", "content": "You are a preference extractor. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                                                temperature=0.3,
                max_tokens=200
            )

            result_text = response.choices[0].message.content.strip()

            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()

            data = json.loads(result_text)
            preferences = data.get("preferences", [])
            
            return {
                **state,
                "preferences": preferences
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"❌ Rate limit hit in preferences, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Preferences Error: {error_msg}")
                return {
                    **state,
                    "preferences": [],
                    "errors": state.get("errors", []) + [f"Preferences extraction failed: {error_msg}"]
                }