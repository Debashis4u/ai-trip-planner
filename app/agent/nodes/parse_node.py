# app/agent/nodes/parse_node.py

import json
import os
import re
from app.agent.groq_client import get_groq_client, create_chat_completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_node(state: dict):
    user_input = state["user_input"]
    existing_date = state.get("start_date")

    try:
        client = get_groq_client()
        response = create_chat_completion(client, 
            messages=[
                {"role": "system", "content": """Extract trip details into JSON. Return ONLY valid JSON, no extra text:
                {
                    "destination": "string",
                    "budget": number or null,
                    "duration": number or null
                }"""},
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
        return {
            **state,
            "destination": result.get("destination"),
            "budget": result.get("budget"),
            "duration": result.get("duration")
        }

    except Exception as e:
        print("❌ Parse Error:", str(e))

        return {
            **state,
            "errors": [str(e)]
        }
