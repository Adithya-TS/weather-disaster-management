"""
FastAPI application exposing the agentic disaster-management workflow.

Run locally:
    uvicorn src.api.fastapi_app:app --reload
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..main import WorkflowExecutor
from ..tools.custom_tools import (
    get_weather_data,
    get_social_media_reports,
    analyze_disaster_type,
    generate_response_plan,
    send_emergency_alerts,
    verify_with_human,
    geocode_location,
)
from ..tools.route_planning import get_route_weather_analysis
from ..tools.seismic_tools import (
    get_earthquake_data,
    get_tsunami_warnings,
    assess_earthquake_risk,
    fact_check_earthquake_claim,
)
from ..memory.session_memory import StateManager, DisasterEvent
from ..evaluation.agent_evaluation import EvaluationSuite
from ..routes.auth_routes import router as auth_router
from ..routes.chat_routes import router as chat_router
from ..routes.alert_routes import router as alert_router
from ..database.connection import init_db, get_db
from ..api.dependencies import get_current_user
from ..services.chat_service import ChatService
from ..api.enhanced_disaster_response import get_enhanced_disaster_analysis
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
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],  # Whitelist UI origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(alert_router)

# Instantiate executor once so sessions, logging, and plugins are reused.
executor = WorkflowExecutor()
state_manager = StateManager(executor.session_service)
evaluation_suite = EvaluationSuite()


# ============================================================================
# Request/Response Models
# ============================================================================

class DisasterRequest(BaseModel):
    location: str = Field(..., min_length=2, description="Location (area, city, village) to analyze")


class DisasterResponse(BaseModel):
    success: bool
    location: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    full_location: Optional[str] = None
    session_id: Optional[str] = None
    response: Optional[str] = None
    raw_response: Optional[str] = None
    duration: Optional[float] = None
    timestamp: str


class AnalyzeRequest(BaseModel):
    location: str = Field(..., min_length=2, description="Location (area, city, village) to analyze")
    weather_data: Optional[str] = Field(None, description="Optional pre-fetched weather data")
    social_reports: Optional[str] = Field(None, description="Optional pre-fetched social media reports")


class PlanRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster")
    severity: str = Field(..., description="Severity level (Critical, High, Medium, Low)")
    location: str = Field(..., min_length=2, description="Affected location (area, city, village)")


class AlertRequest(BaseModel):
    response_plan: str = Field(..., description="The response plan to send as alerts")
    channels: Optional[List[str]] = Field(None, description="Alert channels (defaults to all)")


class EarthquakeRequest(BaseModel):
    location: Optional[str] = Field(None, description="Location name (will be geocoded)")
    latitude: Optional[float] = Field(None, description="Latitude for center of search")
    longitude: Optional[float] = Field(None, description="Longitude for center of search")
    radius_km: int = Field(500, description="Search radius in kilometers")
    min_magnitude: float = Field(2.5, description="Minimum earthquake magnitude")
    days: int = Field(7, description="Number of days to look back")


class TsunamiRequest(BaseModel):
    location: Optional[str] = Field(None, description="Location name (will be geocoded)")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")


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
    # Initialize database tables
    try:
        await init_db()
    except Exception as e:
        logger.error("fastapi.startup.db_init_error", error=str(e))
        # Don't fail startup if DB is not available, but log the error


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

@app.get("/api/v1/weather/{location}", tags=["Tools"])
async def get_weather(
    location: str = Path(..., description="Location (area, city, village)", min_length=2),
    start_date: Optional[str] = Query(None, description="Start date for forecast (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for forecast (YYYY-MM-DD)")
):
    """
    Get weather data for a location (area, city, village).
    Supports both current weather and future forecasts.
    For forecasts, provide both start_date and end_date.
    """
    try:
        weather_data = get_weather_data(location, start_date, end_date)
        
        if isinstance(weather_data, dict) and not weather_data.get("success"):
            error_msg = weather_data.get("error", "Unknown error")
            logger.error("api.weather.error", location=location, error=error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        return {
            "success": True,
            "location": location,
            "weather_data": weather_data,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.weather.error", location=location, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@app.get("/api/v1/social-media/{location}", tags=["Tools"])
async def get_social_media(
    location: str = Path(..., description="Location (area, city, village)", min_length=2),
    context: Optional[str] = Query(None, description="Additional context"),
    date: Optional[str] = Query(None, description="Date for reports (YYYY-MM-DD format)")
):
    """
    Get social media reports for a location.
    Direct access to social media monitoring tool.
    Optionally specify a date to get reports for that specific date.
    """
    try:
        reports = get_social_media_reports(location, context or "", date)
        return {
            "success": True,
            "location": location,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "reports": reports,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.social_media.error", location=location, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch social media reports: {str(e)}")


@app.get("/api/v1/route-weather", tags=["Route Planning"])
async def get_route_weather(
    start: str = Query(..., description="Starting city", min_length=2),
    end: str = Query(..., description="Destination city", min_length=2),
    date: Optional[str] = Query(None, description="Date for forecast (YYYY-MM-DD format)")
):
    """
    Analyze weather conditions along a route between two cities.
    Uses Google Maps Directions API for accurate route detection.
    Returns weather data for all major cities along the route with travel recommendations.
    
    Date:
    - YYYY-MM-DD format (e.g., 2025-11-24)
    - Accepts dates from today up to 3 days ahead
    
    Example: /api/v1/route-weather?start=Chennai&end=Trichy&date=2025-11-25
    """
    try:
        # Validate date if provided
        if date:
            try:
                from datetime import datetime, timedelta
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                max_date = today + timedelta(days=3)
                
                if date_obj < today:
                    raise HTTPException(status_code=400, detail="Date cannot be in the past")
                if date_obj > max_date:
                    raise HTTPException(status_code=400, detail="Date cannot be more than 3 days in the future")
            except ValueError:
                raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")
        
        route_analysis = get_route_weather_analysis(start, end, date)
        return route_analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.route_weather.error", start=start, end=end, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to analyze route weather: {str(e)}")


@app.post("/api/v1/analyze", tags=["Tools"])
async def fact_check_weather_claim(payload: AnalyzeRequest):
    """
    Fact-check weather or seismic claims against official data from reliable sources.
    Verifies user reports/claims with actual meteorological and seismic data.
    """
    try:
        # Geocode location
        geo_data = geocode_location(payload.location)
        if not geo_data:
            raise HTTPException(status_code=400, detail=f"Could not geocode location: {payload.location}")
        
        latitude = geo_data["lat"]
        longitude = geo_data["lon"]
        
        # User's claim
        user_claim = payload.weather_data or payload.social_reports
        
        if not user_claim:
            raise HTTPException(status_code=400, detail="Please provide a weather or seismic claim to verify")
        
        user_claim_lower = user_claim.lower()
        
        # Check if claim is about earthquakes/tsunamis
        is_seismic_claim = any(word in user_claim_lower for word in 
                               ["earthquake", "quake", "tremor", "seismic", "tsunami", "tidal wave"])
        
        if is_seismic_claim:
            # Use seismic fact-checking
            verification = fact_check_earthquake_claim(user_claim, latitude, longitude, payload.location)
            claim_type = "seismic"
        else:
            # Use weather fact-checking
            official_weather = get_weather_data(payload.location)
            from ..tools.custom_tools import fact_check_weather_claim as verify_weather_claim
            verification = verify_weather_claim(user_claim, official_weather, payload.location)
            claim_type = "weather"
        
        return {
            "success": True,
            "location": payload.location,
            "claim_type": claim_type,
            "user_claim": user_claim,
            "verification": verification,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.fact_check.error", location=payload.location, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to verify claim: {str(e)}")


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
            payload.location
        )
        return {
            "success": True,
            "location": payload.location,
            "disaster_type": payload.disaster_type,
            "severity": payload.severity,
            "response_plan": plan,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.plan.error", location=payload.location, error=str(e))
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
    Direct access to alert broadcasting tool.
    """
    try:
        result = send_emergency_alerts(
            payload.response_plan,
            payload.channels
        )
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.alerts.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to send alerts: {str(e)}")


# ============================================================================
# Seismic & Tsunami Monitoring Endpoints
# ============================================================================

@app.post("/api/v1/earthquakes", tags=["Seismic"])
async def get_earthquakes(payload: EarthquakeRequest):
    """
    Get recent earthquake data from USGS.
    Search by location name or coordinates.
    """
    try:
        latitude = payload.latitude
        longitude = payload.longitude
        
        # Geocode location if provided
        if payload.location and (latitude is None or longitude is None):
            geo_data = geocode_location(payload.location)
            if geo_data:
                latitude = geo_data["lat"]
                longitude = geo_data["lon"]
            else:
                raise HTTPException(status_code=400, detail=f"Could not geocode location: {payload.location}")
        
        earthquake_data = get_earthquake_data(
            latitude=latitude,
            longitude=longitude,
            radius_km=payload.radius_km,
            min_magnitude=payload.min_magnitude,
            days=payload.days
        )
        
        # Add risk assessment for each earthquake if location provided
        if latitude is not None and longitude is not None:
            for eq in earthquake_data.get("earthquakes", []):
                if eq.get("latitude") and eq.get("longitude"):
                    # Calculate distance
                    from math import radians, sin, cos, sqrt, atan2
                    R = 6371  # Earth radius in km
                    
                    lat1, lon1 = radians(latitude), radians(longitude)
                    lat2, lon2 = radians(eq["latitude"]), radians(eq["longitude"])
                    
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                    distance = R * c
                    
                    eq["distance_km"] = round(distance, 2)
                    
                    # Add risk assessment
                    if eq.get("magnitude") and eq.get("depth_km"):
                        risk = assess_earthquake_risk(
                            eq["magnitude"],
                            eq["depth_km"],
                            distance
                        )
                        eq["risk_assessment"] = risk
        
        return earthquake_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.earthquakes.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch earthquake data: {str(e)}")


@app.post("/api/v1/tsunami-warnings", tags=["Seismic"])
async def get_tsunami_alerts(payload: TsunamiRequest):
    """
    Get active tsunami warnings from NOAA/NWS.
    Search by location name or coordinates.
    """
    try:
        latitude = payload.latitude
        longitude = payload.longitude
        
        # Geocode location if provided
        if payload.location and (latitude is None or longitude is None):
            geo_data = geocode_location(payload.location)
            if geo_data:
                latitude = geo_data["lat"]
                longitude = geo_data["lon"]
            else:
                raise HTTPException(status_code=400, detail=f"Could not geocode location: {payload.location}")
        
        tsunami_data = get_tsunami_warnings(latitude, longitude)
        
        return tsunami_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.tsunami.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch tsunami warnings: {str(e)}")


@app.post("/api/v1/seismic-fact-check", tags=["Seismic"])
async def seismic_fact_check(payload: AnalyzeRequest):
    """
    Fact-check earthquake/tsunami claims against official USGS and NOAA data.
    """
    try:
        # Geocode location
        geo_data = geocode_location(payload.location)
        if not geo_data:
            raise HTTPException(status_code=400, detail=f"Could not geocode location: {payload.location}")
        
        latitude = geo_data["lat"]
        longitude = geo_data["lon"]
        
        # User's claim (can be in weather_data or social_reports field)
        user_claim = payload.weather_data or payload.social_reports
        
        if not user_claim:
            raise HTTPException(status_code=400, detail="Please provide a seismic claim to verify")
        
        # Fact-check the claim
        verification = fact_check_earthquake_claim(user_claim, latitude, longitude, payload.location)
        
        return {
            "success": True,
            "location": payload.location,
            "user_claim": user_claim,
            "verification": verification,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.seismic_fact_check.error", location=payload.location, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to verify claim: {str(e)}")


# ============================================================================
# Workflow Endpoints (Full Agentic Flow)
# ============================================================================

@app.post(
    "/api/v1/disaster-response",
    response_model=DisasterResponse,
    tags=["Workflow"],
)
async def run_disaster_workflow(
    payload: DisasterRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute enhanced disaster analysis with real-time weather data and severity detection.
    Shows actual weather metrics and automatic severity assessment.
    Requires authentication via JWT token.
    Stores chat history after successful execution.
    """
    logger.info("api.workflow.request", location=payload.location, user_id=user_id)
    
    # Execute enhanced disaster analysis with real weather data
    result = await get_enhanced_disaster_analysis(payload.location, db)

    if not result.get("success"):
        logger.error("api.workflow.failed", location=payload.location, error=result.get("error"))
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    # Save chat history
    try:
        chat_service = ChatService(db)
        input_text = f"Weather disaster analysis for {payload.location}"
        output_text = result.get("response", "")
        model = "enhanced-weather-detector"
        
        await chat_service.save_chat(
            user_id=user_id,
            input_text=input_text,
            output_text=output_text,
            model=model
        )
        logger.info("api.workflow.chat_saved", user_id=user_id, location=payload.location)
    except Exception as e:
        # Log error but don't fail the request
        logger.error("api.workflow.chat_save_error", error=str(e))

    logger.info("api.workflow.completed", location=payload.location)
    
    # Format response to match expected DisasterResponse model
    return DisasterResponse(
        success=True,
        location=payload.location,
        city=result.get("city"),
        state=result.get("state"),
        country=result.get("country"),
        full_location=result.get("location"),
        session_id=result.get("session_id"),
        response=result.get("response"),
        raw_response=result.get("raw_weather_data"),
        duration=result.get("duration", 0.0),
        timestamp=result.get("timestamp")
    )


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.get("/api/v1/sessions", tags=["Sessions"])
async def list_sessions(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of sessions to return"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List recent sessions for the authenticated user.
    Returns sessions from chat history (each workflow execution is a session).
    """
    try:
        chat_service = ChatService(db)
        chat_history = await chat_service.get_user_chat_history(
            user_id=user_id,
            limit=limit,
            offset=0
        )
        
        # Transform chat history into session format
        sessions = []
        for chat in chat_history:
            # Extract location from input text (format: "Analyze and respond to weather disaster situation in {location}")
            input_text = chat.get("input_text", "")
            location = "Unknown"
            if "in " in input_text.lower():
                try:
                    location = input_text.split("in ")[-1].strip()
                except:
                    pass
            
            # Extract disaster info from output if available
            output_text = chat.get("output_text", "")
            disaster_type = None
            severity = None
            
            # Try to extract disaster type and severity from output
            if output_text:
                output_lower = output_text.lower()
                # Common disaster types
                for dt in ["hurricane", "flood", "tornado", "heatwave", "wildfire", "earthquake", "tsunami"]:
                    if dt in output_lower:
                        disaster_type = dt.capitalize()
                        break
                
                # Severity levels
                for sev in ["critical", "high", "medium", "low"]:
                    if sev in output_lower:
                        severity = sev.capitalize()
                        break
            
            session_data = {
                "id": chat.get("id"),
                "session_id": f"session_{chat.get('id')}",  # Generate session_id from chat id
                "city": location,
                "location": location,
                "timestamp": chat.get("created_at"),
                "created_at": chat.get("created_at"),
                "disaster_type": disaster_type,
                "severity": severity,
                "response_plan": chat.get("output_text", "")[:500] if chat.get("output_text") else None,  # Truncate for list view
                "model": chat.get("model"),
                "duration": None,  # Not stored in chat history
            }
            sessions.append(session_data)
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("api.sessions.error", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")


@app.get("/api/v1/sessions/{session_id}", tags=["Sessions"])
async def get_session(
    session_id: str = Path(..., description="Session ID"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get session details and history from chat history.
    Session ID format: session_{chat_id} or just the chat_id number.
    """
    try:
        # Extract chat ID from session_id (format: "session_123" or just "123")
        chat_id_str = session_id.replace("session_", "").strip()
        try:
            chat_id = int(chat_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        # Get chat history entry
        chat_service = ChatService(db)
        chat = await chat_service.get_chat_by_id(chat_id, user_id)
        
        if not chat:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Extract location from input text
        input_text = chat.get("input_text", "")
        location = "Unknown"
        if "in " in input_text.lower():
            try:
                location = input_text.split("in ")[-1].strip()
            except:
                pass
        
        # Extract disaster info from output
        output_text = chat.get("output_text", "")
        disaster_type = None
        severity = None
        
        if output_text:
            output_lower = output_text.lower()
            for dt in ["hurricane", "flood", "tornado", "heatwave", "wildfire", "earthquake", "tsunami"]:
                if dt in output_lower:
                    disaster_type = dt.capitalize()
                    break
            
            for sev in ["critical", "high", "medium", "low"]:
                if sev in output_lower:
                    severity = sev.capitalize()
                    break
        
        return {
            "success": True,
            "session_id": session_id,
            "id": chat.get("id"),
            "city": location,
            "location": location,
            "timestamp": chat.get("created_at"),
            "created_at": chat.get("created_at"),
            "disaster_type": disaster_type,
            "severity": severity,
            "response_plan": chat.get("output_text", ""),
            "model": chat.get("model"),
            "input_text": chat.get("input_text", ""),
            "output_text": chat.get("output_text", ""),
            "duration": None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.session.error", session_id=session_id, user_id=user_id, error=str(e))
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

