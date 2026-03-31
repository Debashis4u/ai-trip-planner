# app/agent/nodes/parse_node.py

import json
import re
from datetime import datetime
from app.agent.groq_client import get_groq_client, create_chat_completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_node(state: dict):
    user_input = state["user_input"]
    existing_date = state.get("start_date")
    today_str = datetime.now().strftime("%Y-%m-%d")
    system_prompt = (
        """Extract trip details into JSON. Return ONLY valid JSON, no extra text:
                {
                    \"destination\": \"string\",
                    \"budget\": number or null,
                    \"duration\": number or null,
                    \"start_date\": \"YYYY-MM-DD\" or null
                }
                Rules:
                - `start_date` must always be ISO format YYYY-MM-DD when present.
                - If user gives a date without year (e.g., \"20th April\"), infer a sensible future date using today="""
        + today_str
        + """.
                - If no date is mentioned, return null for `start_date`.
                """
    )

    try:
        client = get_groq_client()
        response = create_chat_completion(client, 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=200
        )

        result_text = response.choices[0].message.content.strip()

        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group()

        result = json.loads(result_text)
        llm_start_date = result.get("start_date")
        if llm_start_date:
            try:
                llm_start_date = datetime.strptime(llm_start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                llm_start_date = None

        return {
            **state,
            "destination": result.get("destination"),
            "budget": result.get("budget"),
            "duration": result.get("duration"),
            "start_date": existing_date or llm_start_date,
        }

    except Exception as e:
        error_text = str(e)
        print("❌ Parse Error:", error_text)

        if "invalid_api_key" in error_text.lower() or "api key" in error_text.lower():
            error_text = "Groq authentication failed: Invalid API key. Set a valid GROQ_API_KEY in your .env file."

        return {
            **state,
            "errors": state.get("errors", []) + [error_text],
            "is_valid": False,
        }
