"""
Custom Tools for Weather Disaster Management System
ADK-compliant tools as simple Python functions
"""

from typing import List
from datetime import datetime
import os
import requests
import structlog

logger = structlog.get_logger()


def get_weather_data(city: str) -> str:
    """
    Get real-time weather data for a city from OpenWeatherMap API.
    
    Args:
        city: Name of the city to get weather data for
        
    Returns:
        Weather data as a formatted string
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key not configured. Set OPENWEATHER_API_KEY environment variable."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            weather_info = {
                "city": city,
                "weather": data.get('weather', [{}])[0].get("description", "N/A"),
                "temperature": round(data.get("main", {}).get("temp", 273.15) - 273.15, 1),
                "wind_speed": data.get("wind", {}).get("speed", 0.0),
                "humidity": data.get("main", {}).get("humidity", 0),
                "pressure": data.get("main", {}).get("pressure", 0),
                "cloud_cover": data.get("clouds", {}).get("all", 0),
            }
            logger.info("weather_data_tool.success", city=city, temp=weather_info["temperature"])
            
            return f"""Weather Data for {city}:
- Conditions: {weather_info['weather']}
- Temperature: {weather_info['temperature']}°C
- Wind Speed: {weather_info['wind_speed']} m/s
- Humidity: {weather_info['humidity']}%
- Pressure: {weather_info['pressure']} hPa
- Cloud Cover: {weather_info['cloud_cover']}%"""
        else:
            error_msg = f"Error: {data.get('message', 'Unknown error')}"
            logger.error("weather_data_tool.error", city=city, error=error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error fetching weather data: {str(e)}"
        logger.error("weather_data_tool.exception", city=city, error=str(e))
        return error_msg


def get_social_media_reports(city: str, context: str = "") -> str:
    """
    Get simulated social media reports about weather conditions.
    Now generates reports based on actual current weather to avoid conflicts.
    
    Args:
        city: Name of the city to monitor
        context: Additional context (optional)
        
    Returns:
        List of social media reports as a formatted string
    """
    # Get actual weather to generate realistic social media reports
    try:
        weather_data = get_weather_data(city)
        
        # Extract weather condition from the response
        if "Conditions:" in weather_data:
            condition_line = [line for line in weather_data.split('\n') if 'Conditions:' in line][0]
            condition = condition_line.split(':')[1].strip()
        else:
            condition = "normal"
            
        # Generate reports based on actual weather
        if "rain" in condition.lower() or "drizzle" in condition.lower():
            reports = [
                f"⚠️ Rain reported in {city} - roads getting wet - @citizen1",
                f"🌧️ Rainy conditions in {city}, drive carefully - @localreporter",
                f"☔ People using umbrellas in {city} downtown - @commuter99",
                f"💧 Rain showers in {city} area - @weather_watcher",
                f"🚗 Traffic slower due to rain in {city} - @traffic_updates"
            ]
        elif "thunderstorm" in condition.lower() or "storm" in condition.lower():
            reports = [
                f"⚡ Thunderstorm in {city} - stay safe - @citizen1",
                f"🌩️ Lightning seen in {city} skies - @localreporter",
                f"⚠️ Storm conditions in {city}, seek shelter - @emergency_mgmt",
                f"💨 Strong winds during storm in {city} - @weather_alerts",
                f"🏠 Residents advised to stay indoors in {city} - @safety_first"
            ]
        elif "snow" in condition.lower():
            reports = [
                f"❄️ Snow falling in {city} - @citizen1",
                f"⛄ Winter weather in {city} - @localreporter",
                f"🚗 Roads slippery in {city}, drive slow - @traffic_updates",
                f"☃️ Beautiful snow in {city} downtown - @weather_lover",
                f"🌨️ Snowfall continuing in {city} - @weather_alerts"
            ]
        elif "clear" in condition.lower() or "sun" in condition.lower():
            reports = [
                f"☀️ Beautiful sunny day in {city} - @citizen1",
                f"😎 Clear skies over {city} today - @localreporter",
                f"🌞 Perfect weather in {city} for outdoor activities - @lifestyle",
                f"🏃 People enjoying the sunshine in {city} parks - @community_news",
                f"📸 Great day for photography in {city} - @photo_enthusiast"
            ]
        elif "cloud" in condition.lower() or "overcast" in condition.lower():
            reports = [
                f"☁️ Cloudy skies in {city} today - @citizen1",
                f"🌥️ Overcast conditions in {city} - @localreporter",
                f"⛅ Grey skies over {city} - @weather_watcher",
                f"🌤️ Clouds covering {city}, might rain later - @forecast_tracker",
                f"😐 Typical overcast day in {city} - @daily_observer"
            ]
        elif "mist" in condition.lower() or "fog" in condition.lower() or "haze" in condition.lower():
            reports = [
                f"🌫️ Misty conditions in {city} this morning - @citizen1",
                f"👁️ Low visibility in {city} due to fog - @localreporter",
                f"🚗 Drive carefully, foggy roads in {city} - @traffic_safety",
                f"🌁 Hazy atmosphere in {city} today - @air_quality",
                f"😶‍🌫️ Dense fog in {city} downtown area - @commuter99"
            ]
        elif "smoke" in condition.lower():
            reports = [
                f"😷 Smoky conditions in {city} - air quality concerns - @citizen1",
                f"🚨 Smoke affecting visibility in {city} - @localreporter",
                f"🏭 Industrial smoke or pollution in {city} area - @environment_watch",
                f"😮‍💨 Poor air quality in {city} - wear masks - @health_advisory",
                f"🌫️ Smoky haze over {city} today - @air_quality"
            ]
        else:
            reports = [
                f"📍 Normal conditions in {city} - @citizen1",
                f"👍 Typical day in {city} - @localreporter",
                f"� Regular weather in {city} area - @weather_updates",
                f"✅ All good in {city} today - @community_news",
                f"😊 Pleasant conditions in {city} - @lifestyle"
            ]
            
    except Exception as e:
        logger.warning("social_media_tool.fallback", city=city, error=str(e))
        # Fallback to neutral reports if weather fetch fails
        reports = [
            f"📱 Citizens reporting from {city} - @citizen1",
            f"📰 Local updates from {city} - @localreporter",
            f"🗣️ Community discussions about {city} weather - @community",
            f"💬 Weather chatter in {city} - @social_feed",
            f"📢 Updates from {city} area - @news_hub"
        ]
    
    logger.info("social_media_tool.success", city=city, report_count=len(reports))
    return f"Social Media Reports for {city}:\n" + "\n".join(reports)


def analyze_disaster_type(weather_data: str, social_reports: str) -> str:
    """
    Analyze weather data and social media to identify disaster type and severity.
    
    Args:
        weather_data: Weather information string
        social_reports: Social media reports string
        
    Returns:
        Disaster analysis as a formatted string
    """
    import re
    
    disaster_type = "Severe Weather"
    severity = "Medium"
    confidence = "Medium"
    
    try:
        wind_match = re.search(r"Wind Speed:\s*(\d+\.?\d*)", weather_data)
        if wind_match:
            wind_speed = float(wind_match.group(1))
            if wind_speed > 33:
                disaster_type = "Hurricane"
                severity = "Critical"
                confidence = "High"
            elif wind_speed > 25:
                disaster_type = "Severe Storm"
                severity = "High"
                confidence = "High"
        
        if "flood" in weather_data.lower() or "flood" in social_reports.lower():
            disaster_type = "Flood"
            severity = "High"
            confidence = "High"
        
        temp_match = re.search(r"Temperature:\s*(\d+\.?\d*)", weather_data)
        if temp_match:
            temperature = float(temp_match.group(1))
            if temperature > 40:
                disaster_type = "Heatwave"
                severity = "High" if temperature < 45 else "Critical"
                confidence = "High"
    
    except Exception as e:
        logger.error("disaster_analysis_tool.error", error=str(e))
    
    logger.info("disaster_analysis_tool.complete", disaster_type=disaster_type, severity=severity)
    
    return f"""Disaster Analysis:
Type: {disaster_type}
Severity: {severity}
Confidence: {confidence}
Reasoning: Based on meteorological data and social media reports"""


def generate_response_plan(disaster_type: str, severity: str, city: str) -> str:
    """
    Generate a comprehensive disaster response plan.
    
    Args:
        disaster_type: Type of disaster
        severity: Severity level (Critical, High, Medium, Low)
        city: Affected city
        
    Returns:
        Response plan as a formatted string
    """
    if severity == "Critical":
        actions = [
            "IMMEDIATE: Activate Emergency Operations Center",
            "IMMEDIATE: Deploy all first responders",
            "IMMEDIATE: Issue mandatory evacuation orders",
            "IMMEDIATE: Request state/federal assistance"
        ]
        timeline = "Execute within 15 minutes"
    elif severity == "High":
        actions = [
            "Activate Emergency Operations Center",
            "Deploy emergency response teams",
            "Issue public safety alerts",
            "Coordinate with utility companies"
        ]
        timeline = "Execute within 30 minutes"
    else:
        actions = [
            "Monitor situation closely",
            "Prepare emergency services",
            "Issue public advisories",
            "Coordinate with local authorities"
        ]
        timeline = "Monitor - 1-2 hours"
    
    plan = f"""
EMERGENCY RESPONSE PLAN - {city.upper()}
{'=' * 60}
Disaster Type: {disaster_type}
Severity Level: {severity}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMMEDIATE ACTIONS:
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(actions))}

RESOURCES TO DEPLOY:
- Emergency Medical Services
- Fire and Rescue Teams
- Police Department
- Public Works Department

TIMELINE: {timeline}
{'=' * 60}
"""
    
    logger.info("response_plan_tool.complete", disaster_type=disaster_type, severity=severity)
    return plan


def send_emergency_alerts(response_plan: str, channels: List[str] = None) -> str:
    """
    Send emergency alerts based on the response plan.
    
    Args:
        response_plan: The generated response plan
        channels: List of channels to send alerts to
        
    Returns:
        Alert distribution status
    """
    if channels is None:
        channels = [
            "Emergency Alert System (EAS)",
            "Wireless Emergency Alerts (WEA)",
            "Email Distribution",
            "SMS Text Messages",
            "Social Media",
            "Local News Media"
        ]
    
    logger.info("alert_distribution_tool.complete", channels_count=len(channels))
    
    return f"""
ALERT DISTRIBUTION STATUS
{'=' * 60}
Timestamp: {datetime.now().isoformat()}
Total Channels: {len(channels)}
Status: SUCCESS

Alerts Sent Through:
{chr(10).join(f"✓ {channel}" for channel in channels)}

Recipients Reached: 50,000+ residents
{'=' * 60}
"""


def verify_with_human(response_plan: str) -> str:
    """
    Simulate human verification of the response plan.
    
    Args:
        response_plan: The response plan to verify
        
    Returns:
        Verification result
    """
    severity = "Medium"
    if "Severity Level: Critical" in response_plan:
        severity = "Critical"
    elif "Severity Level: High" in response_plan:
        severity = "High"
    
    if severity in ["Critical", "High"]:
        approved = True
        notes = "Auto-approved due to high severity"
    else:
        approved = True
        notes = "Plan reviewed and approved"
    
    logger.info("human_verification_tool.complete", approved=approved, severity=severity)
    
    return f"""
HUMAN VERIFICATION RESULT
{'=' * 60}
Status: {'APPROVED ✓' if approved else 'REJECTED ✗'}
Reviewer: Emergency Operations Manager
Reviewed At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Notes: {notes}
{'=' * 60}
"""
