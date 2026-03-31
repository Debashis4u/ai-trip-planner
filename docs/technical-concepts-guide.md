# Technical Concepts Guide

## 1. FastAPI in This Project

### What it is
FastAPI is the web framework handling HTTP routing and JSON APIs.

### Where used
- app/main.py

### How it works here
- Serves frontend static files and index page
- Exposes POST /plan-trip for trip generation
- Builds initial graph context and invokes graph.invoke(context)

### Why it helps
- Very quick API development
- Pydantic request validation
- Good async ecosystem and production adoption

## 2. LangGraph in This Project

### What it is
LangGraph is a workflow engine for LLM applications with explicit state transitions.

### Where used
- app/agent/graph.py
- app/agent/state.py
- app/agent/nodes/*.py

### How it works here
- StateGraph is built with typed shared state
- Nodes read and write the same state object
- Conditional edges control branching:
  - stop on validation failure
  - loop replanning when over budget

### Why it helps
- Makes multi-step LLM apps deterministic
- Easier debugging than a single large prompt
- Supports retries, fallbacks, and policy checks per node

## 3. Groq LLM Client Pattern

### What it is
A wrapper for Groq chat completion calls with model fallback support.

### Where used
- app/agent/groq_client.py
- consumed by most nodes

### Key behavior
- Reads GROQ_API_KEY from environment
- Uses configured model with optional fallback
- Raises clear errors on auth issues

## 4. State-Driven Architecture

### Concept
All nodes communicate by mutating a shared state dictionary.

### Important fields
- Input: user_input
- Parsed: destination, budget, currency, duration, start_date, end_date
- Enrichment: weather, preferences
- Outputs: plan, accommodation, transportation, packing_list, local_tips
- Control: estimated_cost, is_within_budget, replan_attempts, is_valid, errors

### Benefit
Loose coupling between nodes with explicit contract.

## 5. Node-by-Node Technical Breakdown

### parse_node
- Calls LLM to extract structured JSON fields
- Normalizes currency and date format
- Adds parse/auth errors into state

### validate_node
- Performs deterministic checks (destination, budget, duration, dates)
- Computes end_date when possible
- Can short-circuit flow on critical errors

### preferences_node
- Extracts user interests via LLM
- Uses retry/backoff on rate limits

### weather_node + weather_tool
- Calls wttr.in weather service
- Supports date-aware forecast formatting when date is available

### plan_node
- Generates day-wise itinerary using enriched context
- Uses parsed preferences, weather, budget, currency

### budget_check_node
- Estimates total cost from generated plan
- Compares estimate vs user budget
- Drives replan loop trigger

### replan_node
- Revises itinerary to reduce cost when over budget
- Loop limited by MAX_REPLAN_ATTEMPTS

### accommodation_node and transportation_node
- Adds practical recommendations with budget constraints

### packing_list_node and local_tips_node
- Produces actionable travel prep and local guidance

## 6. Frontend Rendering Model

### Stack
- React + react-dom via esm.sh CDN
- HTM templating instead of JSX build pipeline

### Behavior
- Sends only message to backend
- Renders each response key as a UI section
- Arrays displayed as lists
- Plan and itinerary displayed as numbered lists

## 7. Reliability Patterns in Code

- Node-level exception handling
- Retry with exponential backoff for transient API issues
- Structured JSON enforcement from LLM prompts
- Fallback defaults in selected nodes to maintain user flow

## 8. Key Improvement Opportunities

1. Add schema-level output validation for every node response.
2. Add tracing/metrics around each node execution.
3. Add currency conversion service for mixed-currency scenarios.
4. Add test suite for graph branches and failure paths.
5. Reduce repeated imports and cleanup duplicated os imports in node files.

## 9. How to Explain Core Concepts in 60 Seconds

- FastAPI: API shell and static hosting layer.
- LangGraph: orchestration brain controlling node flow.
- Groq LLM: reasoning and generation engine used by nodes.
- Shared state: memory bus carrying all fields across steps.
- Conditional edges: decision points for stop, continue, or replan.
