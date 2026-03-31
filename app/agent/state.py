from typing import TypedDict, Optional, List

class TripState(TypedDict):
    user_input: str
    destination: Optional[str]
    budget: Optional[int]
    duration: Optional[int]
    start_date: Optional[str]
    end_date: Optional[str]
    weather: Optional[str]
    preferences: Optional[List[str]]
    plan: Optional[List[str]]
    accommodation: Optional[str]
    transportation: Optional[str]
    packing_list: Optional[List[str]]
    local_tips: Optional[List[str]]
    estimated_cost: Optional[int]
    is_within_budget: Optional[bool]
    is_valid: Optional[bool]
    replan_attempts: int
    errors: Optional[List[str]]