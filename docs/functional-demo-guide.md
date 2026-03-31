# Functional Demo Guide

## 1. Demo Goal

Show that the app can turn one natural language request into a complete trip package:
- Parsed trip details
- Weather context
- Itinerary
- Budget fit check
- Accommodation and transport suggestions
- Packing list and local tips

## 2. Before You Demo

1. Ensure environment variable is set in .env:
   - GROQ_API_KEY=your_key
2. Start app:
   - uv run uvicorn app.main:app --reload
3. Open:
   - http://127.0.0.1:8000

## 3. Suggested Demo Script (5 to 7 minutes)

### Step 1: Introduce the value (30 sec)
Say: This app plans a full trip from one prompt and adjusts recommendations based on budget, weather, and preferences.

### Step 2: Enter a rich prompt (45 sec)
Use this message:
Plan a 5 day Goa trip for two people focused on beaches and food under 60000 INR starting 20th April.

Explain that date and currency are extracted from message text.

### Step 3: Generate plan (45 sec)
Click Generate Trip and show loading state.

### Step 4: Walk through result sections (2 to 3 min)
Point out these sections in order:
1. destination, duration, budget, currency, start_date
2. weather
3. plan (numbered days)
4. estimated_cost and budget fit behavior
5. accommodation and transportation
6. packing_list and local_tips as clean bullet lists

### Step 5: Show adaptability (1 to 2 min)
Change prompt to a different style:
Need a 3 day Kyoto temple and street food itinerary under 50000 INR from 24th April.

Explain how the same pipeline adapts with different context.

## 4. Functional Capabilities Checklist

- Natural language parsing of destination, budget, duration, date, currency
- Date extraction from message (no date picker dependency)
- Currency-aware planning prompts
- Multi-node graph execution with validation and conditional routing
- Retry and fallback behavior in several nodes
- Structured output rendering with readable lists

## 5. Demo Talking Points

- Why LangGraph: clear orchestration and conditional control
- Why one API endpoint: simple frontend integration
- Why structured JSON from LLM: predictable downstream processing
- Why weather and budget checks: practical planning quality

## 6. Known Demo Risks and Mitigation

### Risk: Invalid API key
- Symptom: parse/auth errors in response
- Mitigation: verify GROQ_API_KEY before demo

### Risk: LLM rate limits or transient failures
- Symptom: fallback content appears in some sections
- Mitigation: retry once; nodes include retry logic

### Risk: Overly generic output
- Mitigation: use prompts with clear constraints (budget, dates, interests)

## 7. Q and A Prep

### Q: Is this production-ready?
A: It is production-oriented in architecture, but still needs hardening like stronger validation, observability, and pricing data integrations.

### Q: How does it decide what to run?
A: LangGraph manages deterministic node order plus conditional branches for validation and budget replanning.

### Q: Can it support more tools?
A: Yes, new nodes can be added into the graph with explicit state fields and edges.
