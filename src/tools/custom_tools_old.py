"""
Custom Tools for Weather Disaster Management System
Demonstrates: Custom tool creation, MCP integration, built-in tools
"""

from typing import Dict, Any, Optional, List
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import asyncio
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()


class WeatherToolInput(BaseModel):
    """Input schema for weather tool"""
    city: str = Field(..., description="City name to fetch weather data for")
    
    
class WeatherToolOutput(BaseModel):
    """Output schema for weather tool"""
    city: str
    weather: str
    temperature: float
    wind_speed: float
    humidity: int
    pressure: int
    cloud_cover: int
    timestamp: str
    success: bool
    error: Optional[str] = None


class WeatherAPITool:
    """
    Custom Tool: Weather Data Retrieval
    Demonstrates custom tool with retry logic and error handling
    """
    
    name = "weather_api"
    description = "Fetches real-time weather data from OpenWeatherMap API"
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.max_retries = max_retries
        
    async def execute(self, city: str) -> WeatherToolOutput:
        """Execute weather API call with retry logic"""
        logger.info("weather_api_tool.execute", city=city)
        
        for attempt in range(self.max_retries):
            try:
                response = await self._fetch_weather(city)
                data = response.json()
                
                result = WeatherToolOutput(
                    city=city,
                    weather=data.get('weather', [{}])[0].get("description", "N/A"),
                    temperature=round(data.get("main", {}).get("temp", 273.15) - 273.15, 1),
                    wind_speed=data.get("wind", {}).get("speed", 0.0),
                    humidity=data.get("main", {}).get("humidity", 0),
                    pressure=data.get("main", {}).get("pressure", 0),
                    cloud_cover=data.get("clouds", {}).get("all", 0),
                    timestamp=datetime.now().isoformat(),
                    success=True
                )
                
                logger.info("weather_api_tool.success", city=city, attempt=attempt + 1)
                return result
                
            except Exception as e:
                logger.warning(
                    "weather_api_tool.retry",
                    city=city,
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt == self.max_retries - 1:
                    return WeatherToolOutput(
                        city=city,
                        weather="N/A",
                        temperature=0.0,
                        wind_speed=0.0,
                        humidity=0,
                        pressure=0,
                        cloud_cover=0,
                        timestamp=datetime.now().isoformat(),
                        success=False,
                        error=str(e)
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _fetch_weather(self, city: str) -> requests.Response:
        """Internal method to fetch weather data"""
        url = f"{self.base_url}?appid={self.api_key}&q={city}"
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, url)
        response.raise_for_status()
        return response


class EmailAlertTool:
    """
    Custom Tool: Email Alert Dispatcher
    Demonstrates tool with external service integration
    """
    
    name = "email_alert"
    description = "Sends weather disaster alerts via email"
    
    def __init__(
        self,
        sender_email: Optional[str] = None,
        password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587
    ):
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.password = password or os.getenv("EMAIL_PASSWORD")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
    async def execute(
        self,
        recipient: str,
        subject: str,
        body: str,
        severity: str
    ) -> Dict[str, Any]:
        """Send email alert"""
        logger.info("email_alert_tool.execute", recipient=recipient, severity=severity)
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, msg)
            
            logger.info("email_alert_tool.success", recipient=recipient)
            return {
                "success": True,
                "recipient": recipient,
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
            
        except Exception as e:
            logger.error("email_alert_tool.error", recipient=recipient, error=str(e))
            return {
                "success": False,
                "recipient": recipient,
                "error": str(e)
            }
            
    def _send_email(self, msg: MIMEMultipart) -> None:
        """Internal method to send email via SMTP"""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.password)
            server.send_message(msg)


class DataLoggingTool:
    """
    Custom Tool: Data Logger
    Demonstrates tool with file I/O and JSON serialization
    """
    
    name = "data_logger"
    description = "Logs disaster events to persistent storage"
    
    def __init__(self, log_file: str = "disaster_log.json"):
        self.log_file = log_file
        
    async def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log disaster event data"""
        logger.info("data_logger_tool.execute", city=event_data.get("city"))
        
        try:
            # Add timestamp
            event_data["logged_at"] = datetime.now().isoformat()
            
            # Read existing logs
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            # Append new log
            logs.append(event_data)
            
            # Write back
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
            logger.info("data_logger_tool.success", total_logs=len(logs))
            return {
                "success": True,
                "log_count": len(logs),
                "log_file": self.log_file
            }
            
        except Exception as e:
            logger.error("data_logger_tool.error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }


class SocialMediaMonitorTool:
    """
    Custom Tool: Social Media Monitoring (Simulated)
    Demonstrates tool with simulated external API
    """
    
    name = "social_media_monitor"
    description = "Monitors social media for weather-related reports"
    
    SAMPLE_REPORTS = [
        "Local reports of rising water levels and minor flooding.",
        "High winds causing power outages in parts of the city.",
        "Citizens reporting high temperatures and increased heat discomfort.",
        "Social media reports indicate severe storm damage in local infrastructure.",
        "Reports of traffic disruptions due to heavy rain.",
        "No unusual social media reports related to the weather at this time.",
        "Multiple users posting about fallen trees blocking roads.",
        "Emergency services responding to weather-related incidents.",
    ]
    
    async def execute(self, city: str, disaster_type: str) -> List[str]:
        """Fetch simulated social media reports"""
        logger.info("social_media_monitor.execute", city=city, disaster_type=disaster_type)
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Select relevant reports based on disaster type
        import random
        num_reports = random.randint(2, 4)
        reports = random.sample(self.SAMPLE_REPORTS, num_reports)
        
        logger.info("social_media_monitor.success", city=city, report_count=len(reports))
        return reports


class DisasterResearchTool:
    """
    Built-in Tool Integration: Google Search for Disaster Information
    Demonstrates integration with Google's built-in search capabilities
    """
    
    name = "disaster_research"
    description = "Searches for disaster preparedness and response information"
    
    async def execute(self, disaster_type: str, location: str) -> Dict[str, Any]:
        """Search for disaster-specific information"""
        logger.info("disaster_research.execute", disaster_type=disaster_type, location=location)
        
        # In a real implementation, this would use Google Search API
        # For now, we'll return structured guidance
        
        guidelines = {
            "hurricane": {
                "preparation": [
                    "Secure outdoor objects",
                    "Stock emergency supplies",
                    "Identify evacuation routes",
                    "Board up windows"
                ],
                "response": [
                    "Stay indoors away from windows",
                    "Listen to emergency broadcasts",
                    "Do not go outside until all-clear is given"
                ]
            },
            "flood": {
                "preparation": [
                    "Move valuables to higher ground",
                    "Turn off utilities if instructed",
                    "Prepare evacuation kit"
                ],
                "response": [
                    "Move to higher ground immediately",
                    "Avoid walking or driving through flood waters",
                    "Stay away from power lines"
                ]
            },
            "heatwave": {
                "preparation": [
                    "Ensure air conditioning is working",
                    "Stock up on water",
                    "Identify cooling centers"
                ],
                "response": [
                    "Stay hydrated",
                    "Avoid strenuous outdoor activities",
                    "Check on elderly neighbors"
                ]
            }
        }
        
        disaster_key = disaster_type.lower()
        for key in guidelines.keys():
            if key in disaster_key:
                return {
                    "disaster_type": disaster_type,
                    "location": location,
                    "guidelines": guidelines[key],
                    "source": "disaster_research_tool"
                }
        
        return {
            "disaster_type": disaster_type,
            "location": location,
            "guidelines": {
                "preparation": ["Follow local emergency management guidance"],
                "response": ["Stay informed through official channels"]
            },
            "source": "disaster_research_tool"
        }


# Tool Registry
class ToolRegistry:
    """Central registry for all tools"""
    
    def __init__(self):
        self.tools = {
            "weather_api": WeatherAPITool(),
            "email_alert": EmailAlertTool(),
            "data_logger": DataLoggingTool(),
            "social_media_monitor": SocialMediaMonitorTool(),
            "disaster_research": DisasterResearchTool(),
        }
        
    def get_tool(self, name: str):
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
