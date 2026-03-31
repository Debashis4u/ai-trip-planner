def validate_node(state: dict):
    """
    Validate the parsed trip data for consistency and reasonableness.
    """
    destination = state.get("destination")
    budget = state.get("budget")
    duration = state.get("duration")
    start_date = state.get("start_date")
    end_date = state.get("end_date")
    
    errors = state.get("errors", [])
    
    # Validate destination
    if not destination or len(destination.strip()) < 2:
        errors.append("Invalid destination: must be at least 2 characters")
    
    # Validate budget
    if budget is not None:
        if budget <= 0:
            errors.append("Invalid budget: must be positive")
        elif budget > 50000:  # Reasonable upper limit
            errors.append("Budget seems unusually high - please verify")
    
    # Validate duration
    if duration is not None:
        if duration <= 0:
            errors.append("Invalid duration: must be positive")
        elif duration > 30:  # Reasonable upper limit
            errors.append("Duration seems unusually long - please verify")
    
    # Validate dates
    if start_date or end_date:
        try:
            from datetime import datetime, timedelta
            current_date = datetime.now()
            
            if start_date:
                start = datetime.fromisoformat(start_date)
                if start < current_date:
                    errors.append("Start date cannot be in the past")
            
            if end_date:
                end = datetime.fromisoformat(end_date)
                if end < current_date:
                    errors.append("End date cannot be in the past")
                
                if start_date and start >= end:
                    errors.append("End date must be after start date")
            
            # If we have start_date and duration but no end_date, calculate it
            if start_date and duration and not end_date:
                start = datetime.fromisoformat(start_date)
                end = start + timedelta(days=duration - 1)
                end_date = end.isoformat().split("T")[0]  # Format as YYYY-MM-DD
            
            # Check if duration matches dates
            if start_date and end_date and duration:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                calculated_duration = (end - start).days + 1  # inclusive
                if abs(calculated_duration - duration) > 1:  # Allow 1 day tolerance
                    # Auto-correct: if duration is provided, use it to set end_date
                    if duration:
                        end = start + timedelta(days=duration - 1)
                        end_date = end.isoformat().split("T")[0]
                    
        except ValueError as e:
            errors.append(f"Invalid date format: {e}")
    
    # If critical errors, might want to stop processing
    critical_errors = [e for e in errors if "Invalid" in e or "cannot" in e]
    
    return {
        **state,
        "errors": errors,
        "is_valid": len(critical_errors) == 0,
        "end_date": end_date  # Update end_date if it was calculated
    }