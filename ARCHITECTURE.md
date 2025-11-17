# Architecture Diagrams

## System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         User / Scheduler                            │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│                      Main Orchestrator                              │
│                    (WorkflowExecutor)                               │
│  • Session Management  • Observability  • Tool Registry            │
└───────────────────────────┬────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   AGENTS     │   │    TOOLS     │   │   MEMORY     │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Multi-Agent System Flow

```
START
  │
  ▼
┌─────────────────────────────────────┐
│  Parallel Data Collection Agent     │
│  ┌──────────────┐  ┌──────────────┐│
│  │ Weather      │  │ Social Media ││
│  │ Data Agent   │  │ Agent        ││
│  └──────────────┘  └──────────────┘│
└──────────────┬──────────────────────┘
               │ (asyncio.gather)
               ▼
┌─────────────────────────────────────┐
│  Sequential Workflow Agent          │
│  ┌──────────────┐                   │
│  │ 1. Disaster  │                   │
│  │    Analysis  │────┐              │
│  └──────────────┘    │              │
│                      ▼              │
│  ┌──────────────┐                   │
│  │ 2. Severity  │                   │
│  │    Assessment│────┐              │
│  └──────────────┘    │              │
│                      ▼              │
│  ┌──────────────┐                   │
│  │ 3. Response  │                   │
│  │    Generator │                   │
│  └──────────────┘                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Human Verification Agent           │
│  (Long-Running with Pause/Resume)   │
│  ┌──────────────────────────────┐  │
│  │ Low/Medium? → PAUSE → Human  │  │
│  │ High/Critical? → Auto-Approve│  │
│  └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
         [Approved?]
         /          \
       Yes           No
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────┐
│ Send Alerts  │  │ Log Rejection│
│ • Email Tool │  │              │
│ • MCP Multi  │  └──────────────┘
│   Channel    │
└──────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Memory & Logging                    │
│  • Save to Memory Bank               │
│  • Update Session                    │
│  • Record Metrics                    │
└──────────────────────────────────────┘
        │
        ▼
      END
```

## Tools Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Tool Registry                          │
└────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ CUSTOM TOOLS │   │  MCP TOOLS   │   │BUILT-IN TOOLS│
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        │                   │                   │
┌───────┴────────┐  ┌───────┴────────┐  ┌──────┴─────┐
│ WeatherAPI     │  │ MCP Weather    │  │ Disaster   │
│ EmailAlert     │  │ MCP Notify     │  │ Research   │
│ DataLogging    │  │ MCP Aggregator │  │ (Google    │
│ SocialMedia    │  │                │  │  Search)   │
└────────────────┘  └────────────────┘  └────────────┘
```

## Memory System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    State Manager                            │
└────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Session     │   │  Memory      │   │  Context     │
│  Service     │   │  Bank        │   │  Compactor   │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ • Create     │   │ • Store      │   │ • Compact    │
│ • Update     │   │   Events     │   │   History    │
│ • Get        │   │ • Query      │   │ • Reduce     │
│ • Expire     │   │ • Analyze    │   │   Tokens     │
│ • Cleanup    │   │ • Export     │   │ • Preserve   │
│              │   │              │   │   Important  │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Observability Architecture

```
┌────────────────────────────────────────────────────────────┐
│              Observability Manager                          │
└────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┐
        │                   │
        ▼                   ▼
┌──────────────┐   ┌──────────────┐
│   LOGGING    │   │    SESSIONS  │
└──────────────┘   └──────────────┘
        │                   │
        ▼                   ▼
┌──────────────┐   ┌──────────────┐
│ Structured   │   │  ADK Session │
│ JSON Logs    │   │  Management  │
│              │   │              │
│ • Agent      │   │ • State      │
│   Actions    │   │   Tracking   │
│ • Tool Calls │   │ • Memory     │
│ • Workflow   │   │ • Context    │
│   Events     │   │              │
└──────────────┘   └──────────────┘
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Docker Host                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Weather Disaster ADK Container              │ │
│  │  ┌────────────────────────────────────────────────┐  │ │
│  │  │  Application                                    │  │ │
│  │  │  • Multi-Agent System                           │  │ │
│  │  │  • ADK-Compliant Tools                          │  │ │
│  │  │  • ADK Sessions & Memory                        │  │ │
│  │  │  • Structured Logging                           │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  Volumes:                                                   │
│  • ./logs:/app/logs (Application logs)                     │
│  • ./data:/app/data (State persistence)                    │
│                                                             │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                   External Services                         │
│  • OpenWeatherMap API                                      │
│  • Google Gemini API                                       │
└────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
City Name
    │
    ▼
┌─────────────────────┐
│ Parallel Collection │
│   (Weather + SM)    │
└─────────────────────┘
    │
    ▼
Weather Data + Social Media Reports
    │
    ▼
┌─────────────────────┐
│ Disaster Analysis   │
│ (LLM + MCP Context) │
└─────────────────────┘
    │
    ▼
Disaster Type
    │
    ▼
┌─────────────────────┐
│ Severity Assessment │
│ (LLM + Guidelines)  │
└─────────────────────┘
    │
    ▼
Severity Level
    │
    ▼
┌─────────────────────┐
│ Response Generation │
│ (LLM + Research)    │
└─────────────────────┘
    │
    ▼
Response Plan
    │
    ▼
┌─────────────────────┐
│ Human Verification  │
│ (if Low/Medium)     │
└─────────────────────┘
    │
    ▼
Approval Decision
    │
    ▼
┌─────────────────────┐
│ Alert Distribution  │
│ (Email + MCP)       │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Memory Storage      │
│ (Session + Bank)    │
└─────────────────────┘
    │
    ▼
Metrics & Logs
```

## Evaluation Flow

```
┌─────────────────────┐
│ Evaluation Suite    │
└─────────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌─────────┐
│Detection│  │Response │
│Accuracy │  │Quality  │
└─────────┘  └─────────┘
    │             │
    │      ┌──────┴──────┐
    │      │             │
    ▼      ▼             ▼
┌─────────────────────────────┐
│  4 Test Cases:              │
│  • Hurricane (Critical)     │
│  • Flood (High)             │
│  • Heatwave (Medium)        │
│  • Normal Weather (Low)     │
└─────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│ Performance Bench   │
│ • Avg Time          │
│ • Throughput        │
│ • Statistics        │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│ Evaluation Report   │
│ (JSON Output)       │
└─────────────────────┘
```

---

## Legend

- **┌─┐** : Component/Service
- **│**   : Connection/Flow
- **▼**   : Direction of flow
- **───** : Relationship
- **( )** : Description/Details
