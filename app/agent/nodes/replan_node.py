import json
import os
import re
from app.agent.groq_client import get_groq_client, create_chat_completion
import os
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAX_REPLAN_ATTEMPTS = 2

def replan_node(state: dict):
    destination = state.get("destination")
    budget = state.get("budget")
    currency = state.get("currency") or "USD"
    duration = state.get("duration")
    weather = state.get("weather")
    estimated_cost = state.get("estimated_cost")
    replan_attempts = state.get("replan_attempts", 0)

    # Check if we've exceeded max replan attempts
    if replan_attempts >= MAX_REPLAN_ATTEMPTS:
        return {
            **state,
            "replan_attempts": replan_attempts + 1,
            "errors": state.get("errors", []) + ["Max replan attempts reached. Using current plan."]
        }

    try:
        client = get_groq_client()
        
        cost_diff = estimated_cost - budget if estimated_cost else 0
        
        prompt = f"""
        Revise the trip plan for {destination} to fit the budget.
        Duration: {duration} days
        Budget: {budget} {currency}
        Original Estimated Cost: {estimated_cost} {currency}
        Need to reduce by: ~{cost_diff} {currency}
        Weather: {weather}

        Create a {duration}-day itinerary focusing on budget-friendly activities and accommodations.
        Prioritize local experiences and free attractions.
        
        Respond with ONLY a JSON object like: {{"activities": ["Day 1: activity1, activity2", "Day 2: activity3, activity4", ...]}}
        """

        response = create_chat_completion(client, 
                        messages=[
                {"role": "system", "content": "You are a budget-conscious trip planner. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
                                        temperature=0.7,
            max_tokens=1000
        )

        result_text = response.choices[0].message.content.strip()

        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group()

        data = json.loads(result_text)
        activities = data.get("activities", [])
        
        return {
            **state,
            "plan": activities,
            "estimated_cost": None,  # Reset to allow budget check again
            "is_within_budget": None,
            "replan_attempts": replan_attempts + 1
        }

    except Exception as e:
        print(f"❌ Replan Error: {e}")
        return {
            **state,
            "replan_attempts": replan_attempts + 1,
            "errors": state.get("errors", []) + [f"Replan failed: {e}"]
        }
