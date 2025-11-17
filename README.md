# Weather Disaster Management System - Google ADK Implementation

## Overview
This project implements the Weather Disaster Management AI Agent using **Google Agent Development Kit (ADK)**, incorporating advanced multi-agent patterns, tools, memory management, and observability.

## Key Concepts Implemented

### 1. Multi-Agent System ✅
- **Sequential Agents**: Weather data retrieval → Disaster analysis → Severity assessment → Response generation
- **Parallel Agents**: Simultaneous weather API calls and social media monitoring
- **Loop Agents**: Continuous monitoring with scheduled checks

### 2. Tools Integration ✅
- **Custom Tools**: Weather API integration, Email alerting, Data logging
- **MCP (Model Context Protocol)**: External service integration for weather services
- **Built-in Tools**: Google Search for disaster information, Code Execution for data processing

### 3. Sessions & Memory ✅
- **InMemorySessionService**: Manages conversation and workflow state
- **Memory Bank**: Long-term storage of disaster events and patterns
- **Context Engineering**: Context compaction for efficient processing

### 4. Observability ✅
- **Logging**: Comprehensive logging of all agent actions
- **Tracing**: End-to-end tracing of agent workflows
- **Metrics**: Performance metrics for agent execution times and success rates

### 5. Agent Evaluation ✅
- Automated testing of disaster detection accuracy
- Response quality evaluation
- Performance benchmarking

### 6. Long-Running Operations ✅
- Pause/Resume capability for human verification workflows
- Persistent state across sessions

### 7. Agent Deployment ✅
- Docker containerization
- Cloud deployment configuration
- API endpoints for external integration

## Project Structure
```
weather-disaster-adk/
├── src/
│   ├── agents/              # Multi-agent implementations
│   ├── tools/               # Custom tools and MCP integrations
│   ├── memory/              # Session and memory management
│   ├── observability/       # Logging, tracing, metrics
│   ├── evaluation/          # Agent evaluation framework
│   └── utils/               # Utility functions
├── config/                  # Configuration files
├── tests/                   # Test suites
├── deployment/              # Deployment configurations
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECEIVER_EMAIL=recipient@gmail.com
```

## Usage

### Run the Complete System
```bash
python src/main.py
```

### Run with Evaluation
```bash
python src/main.py --evaluate
```

### Run Specific Scenario
```bash
python src/main.py --city "London" --scenario "high"
```

## Architecture

### Agent Flow
1. **Data Collection Agent** (Parallel execution)
   - Weather API Agent
   - Social Media Monitoring Agent

2. **Analysis Agent** (Sequential)
   - Disaster Type Classifier
   - Severity Assessor

3. **Response Generator Agent** (Conditional routing)
   - Emergency Response
   - Civil Defense Response
   - Public Works Response

4. **Verification & Alert Agent** (Long-running with pause/resume)
   - Human Verification (for low/medium severity)
   - Email Alert Dispatcher

5. **Monitoring Loop Agent**
   - Scheduled checks
   - Continuous monitoring

## Features Demonstration

### Multi-Agent Coordination
- Agents communicate through shared state
- Parallel execution for efficiency
- Sequential processing for dependent tasks

### Tool Usage
- Custom weather API tool with retry logic
- MCP integration for external services
- Google Search for disaster research

### Memory Management
- Session persistence across runs
- Historical disaster pattern analysis
- Context-aware decision making

### Observability
- Structured logging with context
- Distributed tracing
- Real-time metrics dashboard

### Evaluation
- Automated accuracy testing
- Response quality scoring
- Performance benchmarking

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_agents.py

# Run with coverage
pytest --cov=src tests/
```

## Deployment

### Docker
```bash
docker build -t weather-disaster-adk .
docker run -p 8080:8080 weather-disaster-adk
```

### Cloud Run (GCP)
```bash
gcloud run deploy weather-disaster-adk \
  --source . \
  --platform managed \
  --region us-central1
```

## License
MIT License

## Author
Adithya - Google ADK Implementation
Original LangGraph Version by Asif
