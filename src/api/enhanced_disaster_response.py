"""Enhanced disaster response with real-time weather data and severity detection."""

from typing import Dict, Any
from datetime import datetime
import structlog

from ..tools.custom_tools import get_weather_data, geocode_location
from ..services.alert_service import AlertService
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger("enhanced_disaster")


async def get_enhanced_disaster_analysis(location: str, db: AsyncSession) -> Dict[str, Any]:
    """
    Get comprehensive disaster analysis with real-time weather data and severity detection.
    
    Args:
        location: Location to analyze
        db: Database session
        
    Returns:
        Dict containing weather data, severity analysis, and recommendations
    """
    import uuid
    from time import time
    
    # Track session and timing
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    start_time = time()
    
    try:
        # 1. Geocode location
        geo_data = geocode_location(location)
        if not geo_data:
            return {
                "success": False,
                "error": f"Could not find location: {location}"
            }
        
        full_location = f"{geo_data.get('name', location)}, {geo_data.get('state', '')}, {geo_data.get('country', '')}".strip(', ')
        
        # 2. Get current weather data
        weather_data = get_weather_data(location)
        if not weather_data or isinstance(weather_data, dict) and not weather_data.get("success"):
            return {
                "success": False,
                "error": "Failed to fetch weather data"
            }
        
        # 3. Use Alert Service to detect severe conditions
        alert_service = AlertService(db)
        alert_data = await alert_service.analyze_weather_for_alerts(location)
        
        # 4. Extract weather metrics
        weather_metrics = alert_service._extract_weather_metrics(weather_data)
        
        # 5. Build comprehensive response
        response = _build_enhanced_response(
            location=full_location,
            geo_data=geo_data,
            weather_metrics=weather_metrics,
            alert_data=alert_data,
            raw_weather=weather_data
        )
        
        # Calculate duration
        duration = time() - start_time
        
        return {
            "success": True,
            "session_id": session_id,
            "duration": round(duration, 2),
            **response
        }
        
    except Exception as e:
        logger.error("enhanced_disaster.error", location=location, error=str(e))
        return {
            "success": False,
            "error": str(e)
        }


def _build_enhanced_response(
    location: str,
    geo_data: Dict,
    weather_metrics: Dict[str, float],
    alert_data: Dict[str, Any] = None,
    raw_weather: Any = None
) -> Dict[str, Any]:
    """Build enhanced response with weather data and severity analysis."""
    
    # Get weather values
    temp = weather_metrics.get("temperature", 0)
    wind = weather_metrics.get("wind_speed", 0)
    precip = weather_metrics.get("precipitation", 0)
    humidity = weather_metrics.get("humidity", 0)
    pressure = weather_metrics.get("pressure", 0)
    
    # Determine conditions
    has_severe_conditions = alert_data is not None
    severity = alert_data.get("severity").value if alert_data else "NORMAL"
    alert_type = alert_data.get("alert_type").value if alert_data else None
    
    # Build formatted response text
    response_parts = []
    
    # Header with severity indicator
    response_parts.append("="*80)
    if has_severe_conditions:
        response_parts.append(f"🚨 SEVERE WEATHER ALERT - {severity.upper()} 🚨")
    else:
        response_parts.append(f"☀️ WEATHER ANALYSIS")
    response_parts.append(f"LOCATION: {location.upper()}")
    response_parts.append("="*80)
    response_parts.append("")
    
    # Check for weather alerts
    weather_alerts = []
    forecast_severity = {}
    if raw_weather and isinstance(raw_weather, dict):
        weather_alerts = raw_weather.get("alerts", [])
        forecast_severity = raw_weather.get("forecast_severity", {})
    
    # Get weather condition for display
    weather_condition = "N/A"
    condition_emoji = "🌈"
    if raw_weather and isinstance(raw_weather, dict):
        weather_condition = raw_weather.get("condition", "N/A")
        cloud_cover = raw_weather.get("cloud_cover", 0)
        
        # Determine emoji based on condition
        condition_lower = weather_condition.lower()
        if "rain" in condition_lower or "drizzle" in condition_lower:
            condition_emoji = "🌧️"
        elif "thunder" in condition_lower or "storm" in condition_lower:
            condition_emoji = "⛈️"
        elif "snow" in condition_lower:
            condition_emoji = "❄️"
        elif "cloud" in condition_lower or cloud_cover > 50:
            condition_emoji = "☁️"
        elif "clear" in condition_lower or cloud_cover < 20:
            condition_emoji = "☀️"
        elif cloud_cover >= 20:
            condition_emoji = "⛅"
    
    # Display official weather alerts if any
    if weather_alerts:
        response_parts.append("🚨 OFFICIAL WEATHER ALERTS:")
        response_parts.append("-" * 80)
        for i, alert in enumerate(weather_alerts, 1):
            response_parts.append(f"⚠️  ALERT #{i}: {alert.get('event', 'Weather Alert')}")
            response_parts.append(f"   Issued by: {alert.get('sender', 'Meteorological Service')}")
            description = alert.get('description', '')
            if description:
                # Truncate long descriptions
                if len(description) > 300:
                    description = description[:300] + "..."
                response_parts.append(f"   {description}")
            response_parts.append("")
    
    # Display forecast warnings if severe
    if forecast_severity.get("has_severe_forecast"):
        response_parts.append("📊 FORECAST WARNING - NEXT 24 HOURS:")
        response_parts.append("-" * 80)
        max_wind = forecast_severity.get("max_wind_24h", 0)
        total_rain = forecast_severity.get("total_precipitation_24h", 0)
        response_parts.append(f"⚠️  Conditions expected to worsen:")
        response_parts.append(f"   • Maximum winds: {max_wind:.1f} km/h")
        response_parts.append(f"   • Total rainfall: {total_rain:.1f} mm")
        
        severe_conditions = forecast_severity.get("severe_conditions", [])
        if severe_conditions:
            response_parts.append(f"   • Severe weather periods: {len(severe_conditions)}")
            for condition in severe_conditions[:3]:  # Show first 3
                response_parts.append(f"     - {condition.get('time', 'N/A')}: {condition.get('condition', 'N/A')}")
        response_parts.append("")
    
    # Current Weather Conditions
    response_parts.append("📊 CURRENT WEATHER CONDITIONS:")
    response_parts.append("-" * 80)
    response_parts.append(f"{condition_emoji}  Condition:      {weather_condition}")
    response_parts.append(f"🌡️  Temperature:    {temp:.1f}°C")
    response_parts.append(f"💨  Wind Speed:     {wind:.1f} km/h")
    response_parts.append(f"🌧️  Precipitation:  {precip:.1f} mm")
    response_parts.append(f"💧  Humidity:       {humidity:.1f}%")
    if pressure > 0:
        response_parts.append(f"🔽  Pressure:       {pressure:.1f} hPa")
    response_parts.append("")
    
    # Severity Analysis
    response_parts.append("⚠️  SEVERITY ANALYSIS:")
    response_parts.append("-" * 80)
    
    if has_severe_conditions:
        response_parts.append(f"❌ SEVERE CONDITIONS DETECTED")
        response_parts.append(f"   Disaster Type: {alert_type.replace('_', ' ').title()}")
        response_parts.append(f"   Severity Level: {severity}")
        response_parts.append("")
        response_parts.append(f"📋 ALERT DETAILS:")
        response_parts.append(f"   {alert_data.get('title')}")
        response_parts.append(f"   {alert_data.get('description')}")
        response_parts.append("")
        
        # Add specific condition warnings
        if temp >= 40:
            response_parts.append(f"   🔥 EXTREME HEAT: {temp:.1f}°C (Dangerous levels)")
        if temp <= -10:
            response_parts.append(f"   ❄️  EXTREME COLD: {temp:.1f}°C (Frostbite risk)")
        if wind >= 118:
            response_parts.append(f"   🌀 HURRICANE FORCE WINDS: {wind:.1f} km/h (Life-threatening)")
        elif wind >= 70:
            response_parts.append(f"   💨 SEVERE WINDS: {wind:.1f} km/h (Structural damage possible)")
        if precip >= 100:
            response_parts.append(f"   🌊 FLASH FLOOD WARNING: {precip:.1f}mm (Immediate danger)")
        elif precip >= 50:
            response_parts.append(f"   🌧️  HEAVY RAINFALL: {precip:.1f}mm (Flooding likely)")
        
    else:
        response_parts.append("✅ NO SEVERE CONDITIONS DETECTED")
        response_parts.append(f"   Current weather is within normal parameters")
        response_parts.append("")
        
        # Show status of each metric
        response_parts.append("📈 CONDITION STATUS:")
        response_parts.append(f"   Temperature: {'⚠️  High' if temp >= 35 else '❄️  Low' if temp <= 0 else '✅ Normal'} ({temp:.1f}°C)")
        response_parts.append(f"   Wind Speed: {'⚠️  High' if wind >= 50 else '✅ Normal'} ({wind:.1f} km/h)")
        response_parts.append(f"   Precipitation: {'⚠️  High' if precip >= 25 else '✅ Normal'} ({precip:.1f} mm)")
        response_parts.append(f"   Humidity: {'⚠️  High' if humidity >= 90 else '✅ Normal'} ({humidity:.1f}%)")
    
    response_parts.append("")
    
    # Safety Recommendations
    response_parts.append("🛡️  SAFETY RECOMMENDATIONS:")
    response_parts.append("-" * 80)
    
    if has_severe_conditions:
        if severity in ["CRITICAL", "HIGH"]:
            response_parts.append("❗ IMMEDIATE ACTION REQUIRED:")
            response_parts.append("   • Seek shelter immediately")
            response_parts.append("   • Stay indoors and away from windows")
            response_parts.append("   • Monitor emergency broadcasts")
            response_parts.append("   • Follow evacuation orders if issued")
            response_parts.append("   • Have emergency supplies ready")
        else:
            response_parts.append("⚠️  PRECAUTIONARY MEASURES:")
            response_parts.append("   • Stay alert to changing conditions")
            response_parts.append("   • Avoid unnecessary travel")
            response_parts.append("   • Secure outdoor objects")
            response_parts.append("   • Monitor weather updates")
    else:
        response_parts.append("✅ STANDARD PRECAUTIONS:")
        response_parts.append("   • Normal activities can continue")
        response_parts.append("   • Stay informed of weather changes")
        response_parts.append("   • Check forecasts before traveling")
    
    response_parts.append("")
    
    # Location Details
    response_parts.append("📍 LOCATION DETAILS:")
    response_parts.append("-" * 80)
    response_parts.append(f"   City/Area: {geo_data.get('name', 'N/A')}")
    if geo_data.get('state'):
        response_parts.append(f"   State/Province: {geo_data.get('state')}")
    response_parts.append(f"   Country: {geo_data.get('country', 'N/A')}")
    response_parts.append(f"   Coordinates: {geo_data.get('lat', 0):.4f}°N, {geo_data.get('lon', 0):.4f}°E")
    response_parts.append("")
    
    # Timestamp
    response_parts.append("="*80)
    response_parts.append(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    response_parts.append("="*80)
    
    formatted_text = "\n".join(response_parts)
    
    return {
        "location": location,
        "city": geo_data.get("name"),
        "state": geo_data.get("state"),
        "country": geo_data.get("country"),
        "coordinates": {
            "latitude": geo_data.get("lat"),
            "longitude": geo_data.get("lon")
        },
        "weather": {
            "temperature": temp,
            "wind_speed": wind,
            "precipitation": precip,
            "humidity": humidity,
            "pressure": pressure
        },
        "severity": {
            "level": severity,
            "has_severe_conditions": has_severe_conditions,
            "alert_type": alert_type,
            "title": alert_data.get("title") if alert_data else None,
            "description": alert_data.get("description") if alert_data else None
        },
        "response": formatted_text,
        "raw_weather_data": str(raw_weather),
        "timestamp": datetime.now().isoformat()
    }

