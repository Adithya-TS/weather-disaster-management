# Weather Disaster Management – Google ADK Agentic Flow

This repository contains a full Google Agent Development Kit (ADK) implementation of a weather-driven disaster-response assistant. The orchestrator coordinates specialized sub-agents, each backed by deterministic tool calls and human-in-the-loop checkpoints, to move from city-level situational awareness to verified emergency alerts.

---

## Stack at a Glance
- **LLM Runtime**: Google ADK `Runner` hosting Gemini `LlmAgent` instances.
- **Agents**: Sequential root coordinator plus specialist sub-agents (data collection, analysis, planning, human verification, alerting).
- **Tools**: Custom weather/social data fetchers, disaster reasoning, response planning, notification simulators, MCP service shims (`src/tools/custom_tools.py`, `src/tools/mcp_integration.py`).
- **State & Memory**: ADK `InMemorySessionService` wrapped by `StateManager` for workflow sessions (`src/memory/session_memory.py`).
- **Observability**: Structured logging + ADK `LoggingPlugin` via `ObservabilityManager` (`src/observability/monitoring.py`).
- **Evaluation**: Scenario accuracy, response quality, and performance benchmarking (`src/evaluation/agent_evaluation.py`).

---

## Repository Layout
```
weather-disaster-management/
├── src/
│   ├── agents/            # Multi-agent graph definitions (new + legacy)
│   ├── tools/             # ADK-compliant tool functions + MCP shims
│   ├── memory/            # Session + workflow state helpers
│   ├── observability/     # Logging + plugin wiring
│   └── evaluation/        # Automated agent test harness
├── tests/                 # Pytest suites (workflow + ADK compliance)
├── requirements.txt       # Runtime dependencies
├── Weather_Disaster_Management_AI_AGENT.ipynb  # Walkthrough notebook
└── README.md              # You are here
```

---

## Agentic Flow (end-to-end)
1. **User Intent**: `WorkflowExecutor` (`src/main.py`) creates a Gemini prompt like “Analyze and respond to weather disaster situation in Miami" and streams it into ADK `Runner`.
2. **Root Coordinator**: `root_disaster_management_agent` enforces the ordered workflow (`src/agents/multi_agent_system.py`):
   - Transfer → `disaster_analyzer_agent`
   - Transfer → `response_planner_agent`
   - Transfer → `verification_agent`
   - Transfer → `alert_agent`
3. **Analysis Stage**: `disaster_analyzer_agent` fans out to tool-powered sub-agents:
   - `weather_data_agent` uses `get_weather_data` (OpenWeatherMap) for live telemetry.
   - `social_media_agent` synthesizes context-aware citizen reports.
   - Tool `analyze_disaster_type` fuses both feeds into a typed/severity-ranked incident.
4. **Response Planning**: `response_planner_agent` calls `generate_response_plan`, producing severity-specific, time-bound checklists covering resources, timelines, and authorities.
5. **Human Verification**: `verification_agent` simulates escalation via `verify_with_human`, ensuring high-severity plans auto-approve while logging reviewer metadata.
6. **Alert Execution**: `alert_agent` calls `send_emergency_alerts` to broadcast across predefined channels and returns the final confirmation to the coordinator.
7. **Observability & Memory**:
   - `ObservabilityManager` writes structured logs + offers ADK `LoggingPlugin` hooks.
   - `StateManager` persists conversation transcripts inside `InMemorySessionService`.
8. **Result Delivery**: Final Gemini response string aggregates the entire workflow summary; `WorkflowExecutor` prints success, duration, and log file path.

---

## Tooling & Integrations
- **Live data**: `get_weather_data` hits OpenWeatherMap with retry-aware logging. Configure `OPENWEATHER_API_KEY`.
- **Synthetic signals**: `get_social_media_reports` mirrors real weather conditions to prevent conflicting narratives.
- **Reasoning utilities**: `analyze_disaster_type`, `generate_response_plan`, `verify_with_human`, `send_emergency_alerts` encode domain logic for deterministic steps.
- **Model Context Protocol (MCP)**: `src/tools/mcp_integration.py` shows how to wrap additional services (context fetch, multi-channel notification, data aggregation) should you need to extend the pipeline beyond built-in tools.

---

## Observability & Evaluation
- `ObservabilityManager` configures structlog sinks (console + rotating JSON files under `logs/`) and exposes an ADK `LoggingPlugin` so every agent event is traced automatically.
- `src/evaluation/agent_evaluation.py` provides:
  - **DisasterDetectionEvaluator**: golden scenarios (hurricane, flood, heatwave, no-threat) for regression checks.
  - **ResponseQualityEvaluator**: heuristic scores for specificity/actionability/completeness/clarity.
  - **PerformanceBenchmark**: throughput + latency stats over repeated executions.

---

## Prerequisites
1. Python 3.10+
2. Google API access with Gemini enabled.
3. OpenWeatherMap API key.

```bash
python -m venv .venv
. .venv/Scripts/activate    # PowerShell
pip install -r requirements.txt
```

Create `.env` (or export values):
```
GOOGLE_API_KEY=your_gemini_key
OPENWEATHER_API_KEY=your_openweather_key
LOG_LEVEL=INFO              # optional
DEMO_CITY=Miami             # optional default for CLI demo
```

---

## Run the Workflow
```bash
python -m src.main          # uses DEMO_CITY or defaults to Miami
```
What you get:
- Console banner describing the target city.
- Structured logs in `logs/disaster_management_*.log`.
- Final status block including agent response text.

To run inside notebooks, open `Weather_Disaster_Management_AI_AGENT.ipynb` and execute the cells (helpful for interactive demos).

### FastAPI REST API
Spin up the HTTP API to access all functionality remotely:
```bash
uvicorn src.api.fastapi_app:app --reload
```
Access interactive API docs at: `http://localhost:8000/docs`

#### System Endpoints
- **`GET /healthz`** – Health check probe
- **`GET /api/v1/status`** – Get system status and agent information

#### Tool Endpoints (Individual Components)
- **`GET /api/v1/weather/{city}`** – Get real-time weather data for a city
- **`GET /api/v1/social-media/{city}`** – Get social media reports for a city
- **`POST /api/v1/analyze`** – Analyze disaster type and severity
  ```json
  {
    "city": "Miami",
    "weather_data": "optional pre-fetched data",
    "social_reports": "optional pre-fetched reports"
  }
  ```
- **`POST /api/v1/plan`** – Generate disaster response plan
  ```json
  {
    "disaster_type": "Hurricane",
    "severity": "Critical",
    "city": "Miami"
  }
  ```
- **`POST /api/v1/verify`** – Verify response plan (human-in-the-loop)
  ```json
  {
    "response_plan": "plan text here"
  }
  ```
- **`POST /api/v1/alerts`** – Send emergency alerts
  ```json
  {
    "response_plan": "plan text here",
    "channels": ["email", "sms", "push"]
  }
  ```

#### Workflow Endpoints (Full Agentic Flow)
- **`POST /api/v1/disaster-response`** – Execute complete workflow
  ```json
  {
    "city": "Miami"
  }
  ```
  Returns: `{success, city, session_id, response, duration, timestamp}`

#### Session Management
- **`GET /api/v1/sessions`** – List sessions (with limit query param)
- **`GET /api/v1/sessions/{session_id}`** – Get session details and history

#### Evaluation Endpoints
- **`POST /api/v1/evaluate`** – Run complete evaluation suite
- **`GET /api/v1/evaluate/benchmark`** – Run performance benchmark only

---

## Testing & Evaluation
```bash
pytest                      # runs test_simple_workflow.py, test_disaster_scenarios.py, etc.
```
For deeper agent scoring, instantiate `EvaluationSuite` and call `run_full_evaluation()` with your executor to capture accuracy + throughput metrics.

---

## Extending the System
- **Add new data feeds**: implement ADK tool wrappers in `src/tools/custom_tools.py` or plug new MCP services into `src/tools/mcp_integration.py`.
- **Customize flow**: edit `src/agents/multi_agent_system.py` to change or reorder sub-agents, or add conditional branching.
- **Persist sessions**: swap `InMemorySessionService` with a durable ADK-compatible backend in `src/memory/session_memory.py`.
- **Deploy**: use the included `Dockerfile`/`docker-compose.yml` or adapt to your infra; the app only depends on ADK-compatible secrets and network access for tools.

---

## Troubleshooting
- Missing API keys → tools return human-readable error strings that bubble up through agents.
- Long latency → adjust `retry_config` or Gemini model (`gemini-2.5-flash-lite` by default).
- Need richer logging → set `LOG_LEVEL=DEBUG` and inspect the generated log file referenced in the CLI output.

Happy building! The codebase is intentionally modular so you can reuse the agents, tools, and observability scaffolding for other ADK projects.
