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

def plan_node(state: dict):
    destination = state.get("destination")
    budget = state.get("budget")
    currency = state.get("currency") or "USD"
    duration = state.get("duration")
    start_date = state.get("start_date")
    end_date = state.get("end_date")
    weather = state.get("weather")
    preferences = state.get("preferences", [])

    if not destination:
        existing_errors = state.get("errors") or []
        return {
            **state,
            "errors": existing_errors + ["No destination provided"]
        }

    date_info = ""
    if start_date and end_date:
        date_info = f" from {start_date} to {end_date}"
    elif start_date:
        date_info = f" starting {start_date}"
    elif end_date:
        date_info = f" ending {end_date}"

    prefs_text = ", ".join(preferences) if preferences else "general interests"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = get_groq_client()
            prompt = f"""
            Create a detailed day-by-day trip plan for {destination}{date_info}.
            Duration: {duration} days
            Budget: {budget} {currency}
            Weather: {weather}
            User preferences: {prefs_text}

            Focus on activities that match the user's interests.
            Make the plan unique and creative, not generic.
            Provide the plan as:

            Day 1: activity1, activity2
            Day 2: activity3, activity4
            ...

            Do not include any other text.
            """

            response = create_chat_completion(client, 
                                messages=[
                    {"role": "system", "content": "You are a helpful trip planner. Provide the plan in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()

            # Debug: print the raw response
            print(f"Plan LLM response: {result_text}")

            # Parse the response as lines starting with "Day "
            activities = []
            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith('Day '):
                    activities.append(line)
            
            # If no activities parsed, use default
            if not activities:
                activities = [
                    f"Day 1: Arrive in {destination}, check into accommodation, explore nearby.",
                    f"Day 2: Visit main attractions in {destination}, try local cuisine.",
                    f"Day 3+: Continue exploring {destination}, depart on last day."
                ]
            
            return {
                **state,
                "plan": activities,
                "replan_attempts": state.get("replan_attempts", 0)
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"❌ Rate limit hit in plan, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                # Fallback: provide a default plan
                default_plan = [
                    f"Day 1: Arrive in {destination}, check into accommodation.",
                    f"Day 2: Explore local attractions in {destination}, depart."
                ]
                return {
                    **state,
                    "plan": default_plan,
                    "errors": state.get("errors", []) + [f"LLM plan generation failed, using default: {error_msg}"]
                }