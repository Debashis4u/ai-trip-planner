import json
import os
import re
from app.agent.groq_client import get_groq_client, create_chat_completion
import os
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def budget_check_node(state: dict):
    destination = state.get("destination")
    budget = state.get("budget")
    duration = state.get("duration")
    plan = state.get("plan", [])

    if not budget or not plan:
        return {
            **state,
            "estimated_cost": None,
            "is_within_budget": True  # Default to True if no budget info
        }

    try:
        client = get_groq_client()

        plan_text = "\n".join(plan)
        
        prompt = f"""
        Analyze this {duration}-day trip plan for {destination} and estimate the total cost in USD.
        Budget: {budget} USD
        
        Trip Plan:
        {plan_text}
        
        Consider: accommodation, food, activities, transportation, and miscellaneous expenses.
        Respond with ONLY a JSON object like: {{"estimated_cost": number, "breakdown": "brief explanation"}}
        """

        response = create_chat_completion(client, 
                        messages=[
                {"role": "system", "content": "You are a budget analyst. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )

        result_text = response.choices[0].message.content.strip()

        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group()

        data = json.loads(result_text)
        estimated_cost = int(data.get("estimated_cost", budget))
        is_within_budget = estimated_cost <= budget

        return {
            **state,
            "estimated_cost": estimated_cost,
            "is_within_budget": is_within_budget
        }

    except Exception as e:
        print(f"❌ Budget Check Error: {e}")
        # Default to True to allow plan through if budget check fails
        return {
            **state,
            "estimated_cost": None,
            "is_within_budget": True,
            "errors": state.get("errors", []) + [f"Budget check failed: {e}"]
        }
