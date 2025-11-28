"""Alert model for weather disaster notifications."""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..database.connection import Base


class SeverityLevel(enum.Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(enum.Enum):
    """Types of disaster alerts."""
    HURRICANE = "hurricane"
    FLOOD = "flood"
    TORNADO = "tornado"
    EARTHQUAKE = "earthquake"
    TSUNAMI = "tsunami"
    HEATWAVE = "heatwave"
    WILDFIRE = "wildfire"
    STORM = "storm"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"
    CYCLONE = "cyclone"


class Alert(Base):
    """Model for weather disaster alerts."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(SeverityLevel), nullable=False, index=True)
    
    # Location information
    location = Column(String(255), nullable=False, index=True)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Alert details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Weather data
    temperature = Column(Float)
    wind_speed = Column(Float)
    precipitation = Column(Float)
    humidity = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_sent = Column(Boolean, default=False, index=True)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type.value}, severity={self.severity.value}, location={self.location})>"

