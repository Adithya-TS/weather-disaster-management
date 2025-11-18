"""
FastAPI application exposing the agentic disaster-management workflow.

Run locally:
    uvicorn src.api.fastapi_app:app --reload
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..main import WorkflowExecutor
from ..tools.custom_tools import (
    get_weather_data,
    get_social_media_reports,
    analyze_disaster_type,
    generate_response_plan,
    send_emergency_alerts,
    verify_with_human,
)
from ..memory.session_memory import StateManager, DisasterEvent
from ..evaluation.agent_evaluation import EvaluationSuite
from fastapi.middleware.cors import CORSMiddleware

logger = structlog.get_logger("fastapi_app")

app = FastAPI(
    title="Weather Disaster Management API",
    description="Agentic AI application for weather disaster management using Google ADK",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3001",  # Whitelist UI origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate executor once so sessions, logging, and plugins are reused.
executor = WorkflowExecutor()
state_manager = StateManager(executor.session_service)
evaluation_suite = EvaluationSuite()


# ============================================================================
# Request/Response Models
# ============================================================================

class DisasterRequest(BaseModel):
    city: str = Field(..., min_length=2, description="City to analyze")


class DisasterResponse(BaseModel):
    success: bool
    city: str
    session_id: Optional[str] = None
    response: Optional[str] = None
    duration: Optional[float] = None
    timestamp: str


class AnalyzeRequest(BaseModel):
    city: str = Field(..., min_length=2, description="City to analyze")
    weather_data: Optional[str] = Field(None, description="Optional pre-fetched weather data")
    social_reports: Optional[str] = Field(None, description="Optional pre-fetched social media reports")


class PlanRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster")
    severity: str = Field(..., description="Severity level (Critical, High, Medium, Low)")
    city: str = Field(..., min_length=2, description="Affected city")


class AlertRequest(BaseModel):
    response_plan: str = Field(..., description="The response plan to send as alerts")
    channels: Optional[List[str]] = Field(None, description="Alert channels (defaults to all)")


class VerifyRequest(BaseModel):
    response_plan: str = Field(..., description="The response plan to verify")


class EvaluationRequest(BaseModel):
    iterations: Optional[int] = Field(10, ge=1, le=100, description="Number of benchmark iterations")


# ============================================================================
# System Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("fastapi.startup", log_file=executor.observability.get_log_file())


@app.get("/healthz", tags=["System"])
async def healthz():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "weather-disaster-management"
    }


@app.get("/api/v1/status", tags=["System"])
async def get_system_status():
    """Get system status and agent information."""
    return {
        "status": "operational",
        "agents": {
            "weather_data_agent": "active",
            "social_media_agent": "active",
            "disaster_analyzer_agent": "active",
            "response_planner_agent": "active",
            "verification_agent": "active",
            "alert_agent": "active",
            "root_coordinator": "active"
        },
        "log_file": executor.observability.get_log_file(),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Tool Endpoints (Individual Components)
# ============================================================================

@app.get("/api/v1/weather/{city}", tags=["Tools"])
async def get_weather(
    city: str = Path(..., description="City name", min_length=2)
):
    """
    Get real-time weather data for a city.
    Direct access to weather data tool.
    """
    try:
        weather_data = get_weather_data(city)
        return {
            "success": True,
            "city": city,
            "weather_data": weather_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.weather.error", city=city, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@app.get("/api/v1/social-media/{city}", tags=["Tools"])
async def get_social_media(
    city: str = Path(..., description="City name", min_length=2),
    context: Optional[str] = Query(None, description="Additional context")
):
    """
    Get social media reports for a city.
    Direct access to social media monitoring tool.
    """
    try:
        reports = get_social_media_reports(city, context or "")
        return {
            "success": True,
            "city": city,
            "reports": reports,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.social_media.error", city=city, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch social media reports: {str(e)}")


@app.post("/api/v1/analyze", tags=["Tools"])
async def analyze_disaster(payload: AnalyzeRequest):
    """
    Analyze disaster type and severity from weather and social media data.
    Can use provided data or fetch fresh data.
    """
    try:
        # Fetch data if not provided
        weather = payload.weather_data or get_weather_data(payload.city)
        social = payload.social_reports or get_social_media_reports(payload.city)
        
        # Analyze
        analysis = analyze_disaster_type(weather, social)
        
        return {
            "success": True,
            "city": payload.city,
            "analysis": analysis,
            "weather_data": weather,
            "social_reports": social,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.analyze.error", city=payload.city, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to analyze disaster: {str(e)}")


@app.post("/api/v1/plan", tags=["Tools"])
async def generate_plan(payload: PlanRequest):
    """
    Generate a disaster response plan.
    Direct access to response planning tool.
    """
    try:
        plan = generate_response_plan(
            payload.disaster_type,
            payload.severity,
            payload.city
        )
        return {
            "success": True,
            "city": payload.city,
            "disaster_type": payload.disaster_type,
            "severity": payload.severity,
            "response_plan": plan,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.plan.error", city=payload.city, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {str(e)}")


@app.post("/api/v1/verify", tags=["Tools"])
async def verify_plan(payload: VerifyRequest):
    """
    Verify a response plan (human-in-the-loop simulation).
    Direct access to verification tool.
    """
    try:
        verification = verify_with_human(payload.response_plan)
        return {
            "success": True,
            "verification": verification,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.verify.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to verify plan: {str(e)}")


@app.post("/api/v1/alerts", tags=["Tools"])
async def send_alerts(payload: AlertRequest):
    """
    Send emergency alerts through multiple channels.
    Direct access to alert distribution tool.
    """
    try:
        alert_status = send_emergency_alerts(
            payload.response_plan,
            payload.channels
        )
        return {
            "success": True,
            "alert_status": alert_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.alerts.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to send alerts: {str(e)}")


# ============================================================================
# Workflow Endpoints (Full Agentic Flow)
# ============================================================================

@app.post(
    "/api/v1/disaster-response",
    response_model=DisasterResponse,
    tags=["Workflow"],
)
async def run_disaster_workflow(payload: DisasterRequest):
    """
    Execute the complete disaster-management workflow for a city.
    This runs the full agentic AI pipeline: analysis → planning → verification → alerts.
    """
    logger.info("api.workflow.request", city=payload.city)
    result = await executor.execute(payload.city)

    if not result.get("success"):
        logger.error("api.workflow.failed", city=payload.city, error=result.get("error"))
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    logger.info("api.workflow.completed", city=payload.city, session_id=result.get("session_id"))
    return result


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.get("/api/v1/sessions", tags=["Sessions"])
async def list_sessions(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of sessions to return")
):
    """
    List recent sessions (limited implementation - returns session info).
    """
    return {
        "success": True,
        "message": "Session listing - full implementation requires persistent storage",
        "note": "Current implementation uses InMemorySessionService",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/sessions/{session_id}", tags=["Sessions"])
async def get_session(
    session_id: str = Path(..., description="Session ID")
):
    """
    Get session details and history.
    """
    try:
        session = await executor.session_service.get_session(
            app_name=executor.app_name,
            user_id=executor.user_id,
            session_id=session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "session": {
                "id": session_id,
                "app_name": executor.app_name,
                "user_id": executor.user_id,
                "message_count": len(session.messages) if hasattr(session, 'messages') else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.session.error", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


# ============================================================================
# Evaluation Endpoints
# ============================================================================

@app.post("/api/v1/evaluate", tags=["Evaluation"])
async def run_evaluation(payload: EvaluationRequest):
    """
    Run the complete evaluation suite (disaster detection + performance benchmark).
    This tests agent accuracy and performance.
    """
    try:
        logger.info("api.evaluation.start", iterations=payload.iterations)
        
        # Note: This requires adapting the evaluation suite to work with WorkflowExecutor
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Evaluation suite - requires executor adaptation",
            "note": "Use the evaluation module directly for full testing",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.evaluation.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to run evaluation: {str(e)}")


@app.get("/api/v1/evaluate/benchmark", tags=["Evaluation"])
async def run_benchmark(
    iterations: int = Query(10, ge=1, le=100, description="Number of iterations")
):
    """
    Run performance benchmark only.
    """
    try:
        from ..evaluation.agent_evaluation import PerformanceBenchmark
        benchmark = PerformanceBenchmark()
        
        # Note: This requires executor adaptation
        return {
            "success": True,
            "message": "Benchmark requires executor adaptation",
            "iterations": iterations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.benchmark.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to run benchmark: {str(e)}")

