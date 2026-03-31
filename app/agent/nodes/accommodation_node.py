import time
from app.agent.groq_client import get_groq_client, create_chat_completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def accommodation_node(state: dict):
    destination = state.get("destination")
    budget = state.get("budget")
    duration = state.get("duration")
    start_date = state.get("start_date")
    end_date = state.get("end_date")
    preferences = state.get("preferences", [])

    if not destination:
        return {
            **state,
            "accommodation": "No destination specified"
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
            Suggest specific accommodation options for a {duration}-day trip to {destination}{date_info}.
            Budget: {budget} USD total
            Preferences: {prefs_text}
            
            Suggest 3 specific, real hotels/resorts/hostels with:
            - Exact hotel name
            - Location/area
            - Estimated nightly rate in USD
            - Total cost for {duration} nights
            - Why it fits the budget and preferences
            
            Focus on budget-friendly options that match the user's interests.
            Include a mix of hotel types (boutique, resort, hostel, etc.).
            
            Provide detailed recommendations with booking considerations.
            """

            response = create_chat_completion(client, 
                                messages=[
                    {"role": "system", "content": "You are an accommodation expert. Provide detailed accommodation recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )

            result_text = response.choices[0].message.content.strip()
            
            return {
                **state,
                "accommodation": result_text
            }

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"❌ Rate limit hit in accommodation, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Accommodation Error: {error_msg}")
                return {
                    **state,
                    "accommodation": f"Budget hotel/hostel in {destination} (~$30-50/night)",
                    "errors": state.get("errors", []) + [f"Accommodation suggestion failed: {error_msg}"]
                }