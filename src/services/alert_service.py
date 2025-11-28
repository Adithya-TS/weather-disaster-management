"""Alert service for monitoring and detecting severe weather conditions."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import structlog

from ..models import Alert, SeverityLevel, AlertType
from ..tools.custom_tools import get_weather_data, geocode_location

logger = structlog.get_logger("alert_service")


class AlertService:
    """Service for creating and managing weather alerts."""
    
    # Thresholds for severe weather conditions
    SEVERE_THRESHOLDS = {
        "temperature_high": 40.0,  # °C
        "temperature_low": -10.0,   # °C
        "wind_speed_high": 70.0,    # km/h (~ 20 m/s)
        "wind_speed_critical": 118.0,  # km/h (~ 33 m/s) - hurricane force
        "precipitation_high": 15.0,  # mm (heavy rain)
        "precipitation_moderate": 5.0,  # mm (moderate rain)
        "precipitation_critical": 50.0,  # mm (extreme flooding risk)
        "humidity_high": 95.0,      # %
        "cloud_cover_full": 90.0,   # % (overcast)
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_weather_for_alerts(
        self, 
        location: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze weather data for a location and determine if alert is needed.
        
        Args:
            location: Location to analyze
            
        Returns:
            Alert data if severe conditions detected, None otherwise
        """
        try:
            # Get weather data
            weather_data = get_weather_data(location)
            
            if not weather_data or isinstance(weather_data, dict) and not weather_data.get("success"):
                logger.warning("alert_service.weather_fetch_failed", location=location)
                return None
            
            # Get geocoded location
            geo_data = geocode_location(location)
            if not geo_data:
                logger.warning("alert_service.geocode_failed", location=location)
                return None
            
            # Extract weather metrics
            weather_info = self._extract_weather_metrics(weather_data)
            
            # Analyze for severe conditions
            alert_data = self._analyze_conditions(
                weather_info,
                location,
                geo_data,
                weather_data  # Pass raw weather data for alerts/forecast
            )
            
            if alert_data:
                logger.info("alert_service.severe_weather_detected", 
                           location=location, 
                           alert_type=alert_data.get("alert_type"),
                           severity=alert_data.get("severity"))
            
            return alert_data
            
        except Exception as e:
            logger.error("alert_service.analysis_error", location=location, error=str(e))
            return None
    
    def _extract_weather_metrics(self, weather_data: Any) -> Dict[str, float]:
        """Extract relevant weather metrics from weather data."""
        metrics = {
            "temperature": 0.0,
            "wind_speed": 0.0,
            "precipitation": 0.0,
            "humidity": 0.0,
            "pressure": 0.0,
            "cloud_cover": 0.0,
        }
        
        try:
            if isinstance(weather_data, str):
                # Parse string data (from API response)
                import re
                temp_match = re.search(r'temperature[:\s]+(-?\d+\.?\d*)', weather_data.lower())
                wind_match = re.search(r'wind[:\s]+(\d+\.?\d*)', weather_data.lower())
                precip_match = re.search(r'precipitation[:\s]+(\d+\.?\d*)', weather_data.lower())
                humid_match = re.search(r'humidity[:\s]+(\d+\.?\d*)', weather_data.lower())
                cloud_match = re.search(r'cloud[:\s]+(\d+\.?\d*)', weather_data.lower())
                
                if temp_match:
                    metrics["temperature"] = float(temp_match.group(1))
                if wind_match:
                    metrics["wind_speed"] = float(wind_match.group(1))
                if precip_match:
                    metrics["precipitation"] = float(precip_match.group(1))
                if humid_match:
                    metrics["humidity"] = float(humid_match.group(1))
                if cloud_match:
                    metrics["cloud_cover"] = float(cloud_match.group(1))
            elif isinstance(weather_data, dict):
                metrics["temperature"] = float(weather_data.get("temperature", 0))
                metrics["wind_speed"] = float(weather_data.get("wind_speed", 0))
                metrics["precipitation"] = float(weather_data.get("precipitation", 0))
                metrics["humidity"] = float(weather_data.get("humidity", 0))
                metrics["cloud_cover"] = float(weather_data.get("cloud_cover", 0))
                
                # Also check weather condition for rain indicators
                condition = weather_data.get("condition", "").lower()
                weather_desc = weather_data.get("weather", "").lower()
                
                # Check for weather alerts and forecast severity
                weather_alerts = weather_data.get("alerts", [])
                forecast_severity = weather_data.get("forecast_severity", {})
                
                # If we have weather alerts or severe forecast, use that data
                if weather_alerts or forecast_severity.get("has_severe_forecast"):
                    # Use forecast data for better precipitation estimate
                    if forecast_severity.get("total_precipitation_24h", 0) > 30:
                        metrics["precipitation"] = max(metrics["precipitation"], forecast_severity.get("max_precipitation_3h", 15.0))
                    if forecast_severity.get("max_wind_24h", 0) > metrics["wind_speed"]:
                        metrics["wind_speed"] = max(metrics["wind_speed"], forecast_severity.get("max_wind_24h", 0))
                
                # If condition indicates rain but precipitation is 0, estimate based on condition
                if metrics["precipitation"] == 0 and any(word in condition or word in weather_desc 
                                                          for word in ["rain", "drizzle", "shower", "thunderstorm"]):
                    # Estimate precipitation based on rain type
                    if "heavy" in condition or "heavy" in weather_desc:
                        metrics["precipitation"] = 15.0  # Estimate heavy rain
                    elif "moderate" in condition or "moderate" in weather_desc:
                        metrics["precipitation"] = 8.0   # Estimate moderate rain
                    elif "light" in condition or "light" in weather_desc or "drizzle" in condition:
                        metrics["precipitation"] = 3.0   # Estimate light rain
                    else:
                        metrics["precipitation"] = 5.0   # Default rain estimate
                        
        except (ValueError, AttributeError) as e:
            logger.warning("alert_service.metric_extraction_error", error=str(e))
        
        return metrics
    
    def _analyze_conditions(
        self,
        metrics: Dict[str, float],
        location: str,
        geo_data: Dict[str, Any],
        weather_data: Any = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze weather metrics and determine alert type and severity."""
        
        temp = metrics.get("temperature", 0)
        wind_speed = metrics.get("wind_speed", 0)
        precipitation = metrics.get("precipitation", 0)
        humidity = metrics.get("humidity", 0)
        cloud_cover = metrics.get("cloud_cover", 0)
        
        # Check for weather alerts from meteorological services
        weather_alerts = []
        forecast_severity = {}
        if isinstance(weather_data, dict):
            weather_alerts = weather_data.get("alerts", [])
            forecast_severity = weather_data.get("forecast_severity", {})
        
        # CRITICAL: Official weather alerts (cyclones, hurricanes, red alerts)
        if weather_alerts:
            alert_event = weather_alerts[0].get("event", "Weather Alert")
            alert_description = weather_alerts[0].get("description", "")
            
            # Determine severity from alert
            severity = SeverityLevel.CRITICAL
            if any(word in alert_event.lower() for word in ["watch", "advisory", "yellow"]):
                severity = SeverityLevel.HIGH
            elif any(word in alert_event.lower() for word in ["warning", "red", "cyclone", "hurricane"]):
                severity = SeverityLevel.CRITICAL
            
            return self._create_alert_data(
                AlertType.HURRICANE if any(w in alert_event.lower() for w in ["cyclone", "hurricane", "typhoon"]) else AlertType.STORM,
                severity,
                f"⚠️ OFFICIAL ALERT: {alert_event}",
                f"{alert_description}\n\n"
                f"Current conditions: {temp:.1f}°C, {wind_speed:.1f} km/h winds, {precipitation:.1f}mm rain, {humidity:.0f}% humidity. "
                f"Follow official guidance and evacuation orders. Stay informed through official channels.",
                location, geo_data, metrics
            )
        
        # CRITICAL/HIGH: Severe forecast conditions (cyclone approaching, major storm)
        if forecast_severity.get("has_severe_forecast"):
            max_wind_24h = forecast_severity.get("max_wind_24h", 0)
            total_precip_24h = forecast_severity.get("total_precipitation_24h", 0)
            severe_conditions = forecast_severity.get("severe_conditions", [])
            
            if max_wind_24h > 100 or total_precip_24h > 50 or any("cyclone" in str(c).lower() or "hurricane" in str(c).lower() for c in severe_conditions):
                return self._create_alert_data(
                    AlertType.HURRICANE,
                    SeverityLevel.CRITICAL,
                    "⚠️ SEVERE WEATHER WARNING - Dangerous Conditions Approaching",
                    f"Severe weather system approaching with {max_wind_24h:.1f} km/h winds and {total_precip_24h:.1f}mm rainfall expected in next 24 hours. "
                    f"Current: {temp:.1f}°C, {wind_speed:.1f} km/h winds, {precipitation:.1f}mm rain, {humidity:.0f}% humidity, {cloud_cover:.0f}% clouds. "
                    f"⚠️ HIGH RISK OF FLOODING, LANDSLIDES, AND FALLING TREES. "
                    f"Avoid unnecessary travel. Stay indoors. Follow local authority instructions. Have emergency supplies ready.",
                    location, geo_data, metrics
                )
            elif max_wind_24h > 60 or total_precip_24h > 30:
                return self._create_alert_data(
                    AlertType.STORM,
                    SeverityLevel.HIGH,
                    "⚠️ SEVERE WEATHER ALERT - Storm Approaching",
                    f"Severe weather forecast with {max_wind_24h:.1f} km/h winds and {total_precip_24h:.1f}mm rainfall expected in next 24 hours. "
                    f"Current: {temp:.1f}°C, {wind_speed:.1f} km/h winds, {precipitation:.1f}mm rain, {humidity:.0f}% humidity. "
                    f"Flooding possible. Secure outdoor objects. Avoid travel if possible. Monitor weather updates closely.",
                    location, geo_data, metrics
                )
        
        # Check for various severe weather conditions
        
        # CRITICAL: Hurricane/Cyclone conditions
        if wind_speed >= self.SEVERE_THRESHOLDS["wind_speed_critical"]:
            return self._create_alert_data(
                AlertType.HURRICANE,
                SeverityLevel.CRITICAL,
                "Hurricane Force Winds Detected",
                f"Extremely dangerous wind speeds of {wind_speed:.1f} km/h detected. "
                f"Seek shelter immediately. Severe structural damage possible.",
                location, geo_data, metrics
            )
        
        # CRITICAL: Extreme heat
        if temp >= self.SEVERE_THRESHOLDS["temperature_high"]:
            return self._create_alert_data(
                AlertType.HEATWAVE,
                SeverityLevel.CRITICAL if temp >= 45 else SeverityLevel.HIGH,
                "Extreme Heat Warning",
                f"Dangerous heat conditions with temperature at {temp:.1f}°C. "
                f"Stay hydrated and avoid prolonged outdoor exposure.",
                location, geo_data, metrics
            )
        
        # CRITICAL: Extreme rainfall/flooding risk
        if precipitation >= self.SEVERE_THRESHOLDS["precipitation_critical"]:
            return self._create_alert_data(
                AlertType.FLOOD,
                SeverityLevel.CRITICAL,
                "Flash Flood Warning",
                f"Extremely heavy rainfall of {precipitation:.1f}mm detected. "
                f"Flash flooding likely. Move to higher ground immediately.",
                location, geo_data, metrics
            )
        
        # HIGH/MEDIUM: Heavy rainfall
        if precipitation >= self.SEVERE_THRESHOLDS["precipitation_high"]:
            severity = SeverityLevel.HIGH if precipitation >= 25 else SeverityLevel.MEDIUM
            return self._create_alert_data(
                AlertType.HEAVY_RAIN,
                severity,
                "Heavy Rainfall Alert",
                f"Heavy rainfall of {precipitation:.1f}mm detected with {humidity:.0f}% humidity. "
                f"Flooding possible in low-lying areas. Roads may be slippery. Exercise caution while traveling.",
                location, geo_data, metrics
            )
        
        # MEDIUM: Moderate rain with very high humidity and full cloud cover
        if (precipitation >= self.SEVERE_THRESHOLDS["precipitation_moderate"] and 
            humidity >= 85 and cloud_cover >= self.SEVERE_THRESHOLDS["cloud_cover_full"]):
            return self._create_alert_data(
                AlertType.HEAVY_RAIN,
                SeverityLevel.MEDIUM,
                "Severe Weather - Heavy Rain Expected",
                f"Active rainfall of {precipitation:.1f}mm detected with {humidity:.0f}% humidity and {cloud_cover:.0f}% cloud cover. "
                f"Wet roads and reduced visibility. Drive carefully and expect slower traffic. "
                f"Conditions may worsen - monitor weather updates.",
                location, geo_data, metrics
            )
        
        # HIGH: Severe storm (high winds + rain)
        if wind_speed >= self.SEVERE_THRESHOLDS["wind_speed_high"] and precipitation >= 5:
            return self._create_alert_data(
                AlertType.STORM,
                SeverityLevel.HIGH,
                "Severe Storm Warning",
                f"Severe storm conditions with {wind_speed:.1f} km/h winds and heavy rain. "
                f"Stay indoors and secure loose objects.",
                location, geo_data, metrics
            )
        
        # MEDIUM: High winds
        if wind_speed >= self.SEVERE_THRESHOLDS["wind_speed_high"]:
            return self._create_alert_data(
                AlertType.STORM,
                SeverityLevel.MEDIUM,
                "High Wind Advisory",
                f"Strong winds of {wind_speed:.1f} km/h expected. "
                f"Secure outdoor objects and use caution while driving.",
                location, geo_data, metrics
            )
        
        # LOW: Extreme cold
        if temp <= self.SEVERE_THRESHOLDS["temperature_low"]:
            return self._create_alert_data(
                AlertType.SNOW,
                SeverityLevel.MEDIUM if temp <= -20 else SeverityLevel.LOW,
                "Extreme Cold Warning",
                f"Dangerously cold temperature of {temp:.1f}°C. "
                f"Frostbite and hypothermia risk. Dress warmly.",
                location, geo_data, metrics
            )
        
        # No severe conditions detected
        return None
    
    def _create_alert_data(
        self,
        alert_type: AlertType,
        severity: SeverityLevel,
        title: str,
        description: str,
        location: str,
        geo_data: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Create alert data dictionary."""
        return {
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "description": description,
            "location": location,
            "city": geo_data.get("name", ""),
            "state": geo_data.get("state", ""),
            "country": geo_data.get("country", ""),
            "latitude": geo_data.get("lat"),
            "longitude": geo_data.get("lon"),
            "temperature": metrics.get("temperature"),
            "wind_speed": metrics.get("wind_speed"),
            "precipitation": metrics.get("precipitation"),
            "humidity": metrics.get("humidity"),
        }
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """
        Create and save a new alert to the database.
        
        Args:
            alert_data: Alert information
            
        Returns:
            Created Alert object
        """
        try:
            # Check if similar active alert exists (within last 6 hours)
            recent_time = datetime.utcnow() - timedelta(hours=6)
            
            stmt = select(Alert).where(
                and_(
                    Alert.location == alert_data["location"],
                    Alert.alert_type == alert_data["alert_type"],
                    Alert.is_active == True,
                    Alert.detected_at >= recent_time
                )
            )
            result = await self.db.execute(stmt)
            existing_alert = result.scalar_one_or_none()
            
            if existing_alert:
                logger.info("alert_service.duplicate_alert_skipped", 
                           location=alert_data["location"],
                           alert_type=alert_data["alert_type"].value)
                return existing_alert
            
            # Create new alert
            alert = Alert(
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                title=alert_data["title"],
                description=alert_data["description"],
                location=alert_data["location"],
                city=alert_data.get("city"),
                state=alert_data.get("state"),
                country=alert_data.get("country"),
                latitude=alert_data.get("latitude"),
                longitude=alert_data.get("longitude"),
                temperature=alert_data.get("temperature"),
                wind_speed=alert_data.get("wind_speed"),
                precipitation=alert_data.get("precipitation"),
                humidity=alert_data.get("humidity"),
                is_active=True,
                is_sent=False,
                detected_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            self.db.add(alert)
            await self.db.commit()
            await self.db.refresh(alert)
            
            logger.info("alert_service.alert_created", 
                       alert_id=alert.id,
                       location=alert.location,
                       severity=alert.severity.value)
            
            return alert
            
        except Exception as e:
            await self.db.rollback()
            logger.error("alert_service.create_error", error=str(e))
            raise
    
    async def get_active_alerts(
        self, 
        location: Optional[str] = None,
        severity: Optional[SeverityLevel] = None
    ) -> List[Alert]:
        """
        Get active alerts, optionally filtered by location and/or severity.
        
        Args:
            location: Filter by location
            severity: Filter by minimum severity
            
        Returns:
            List of active alerts
        """
        try:
            conditions = [Alert.is_active == True]
            
            if location:
                conditions.append(Alert.location.ilike(f"%{location}%"))
            
            if severity:
                severity_order = {
                    SeverityLevel.LOW: 0,
                    SeverityLevel.MEDIUM: 1,
                    SeverityLevel.HIGH: 2,
                    SeverityLevel.CRITICAL: 3
                }
                min_level = severity_order[severity]
                severity_conditions = [
                    Alert.severity == level 
                    for level, order in severity_order.items() 
                    if order >= min_level
                ]
                conditions.append(or_(*severity_conditions))
            
            stmt = select(Alert).where(and_(*conditions)).order_by(Alert.detected_at.desc())
            result = await self.db.execute(stmt)
            alerts = result.scalars().all()
            
            return list(alerts)
            
        except Exception as e:
            logger.error("alert_service.get_alerts_error", error=str(e))
            return []
    
    async def mark_alert_as_sent(self, alert_id: int) -> bool:
        """Mark an alert as sent."""
        try:
            stmt = select(Alert).where(Alert.id == alert_id)
            result = await self.db.execute(stmt)
            alert = result.scalar_one_or_none()
            
            if alert:
                alert.is_sent = True
                alert.sent_at = datetime.utcnow()
                await self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error("alert_service.mark_sent_error", alert_id=alert_id, error=str(e))
            return False

