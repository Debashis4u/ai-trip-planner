import json
import re
import time
from app.agent.groq_client import get_groq_client, create_chat_completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def local_tips_node(state: dict):
    destination = state.get("destination")
    preferences = state.get("preferences", [])

    if not destination:
        return {
            **state,
            "local_tips": ["Research local customs and laws"]
        }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = get_groq_client()
            
            prefs_text = ", ".join(preferences) if preferences else "general"
            
            prompt = f"""
            Provide local tips and advice for visiting {destination}.
            User preferences: {prefs_text}
            
            Include cultural etiquette, safety tips, transportation advice, 
            local customs, best times to visit attractions, and money-saving tips.
            
            Respond with ONLY a JSON object like: {{"local_tips": ["tip1", "tip2", ...]}}
            """

            response = create_chat_completion(client, 
                                messages=[
                    {"role": "system", "content": "You are a local expert. Return ONLY valid JSON."},
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

            local_tips = []
            try:
                data = json.loads(result_text)
                local_tips = data.get("local_tips", [])
            except json.JSONDecodeError:
                print(f"⚠️ Local tips JSON parse failed, using fallback: {result_text}")
                local_tips = [
                    "Learn basic local phrases",
                    "Respect local customs",
                    "Stay aware of surroundings",
                    "Try local transportation"
                ]

            return {
                **state,
                "local_tips": local_tips
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"❌ Rate limit hit in local_tips, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Local Tips Error: {error_msg}")
                return {
                    **state,
                    "local_tips": [
                        "Learn basic local phrases",
                        "Respect local customs",
                        "Stay aware of surroundings",
                        "Try local transportation"
                    ],
                    "errors": state.get("errors", []) + [f"Local tips generation failed: {error_msg}"]
                }