"""User subscription model for alert notifications."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database.connection import Base


class UserSubscription(Base):
    """Model for user alert subscriptions."""
    
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Location to monitor
    location = Column(String(255), nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    radius_km = Column(Float, default=50.0)  # Alert radius in kilometers
    
    # Notification preferences
    email_enabled = Column(Boolean, default=True)
    phone_number = Column(String(20))  # For SMS notifications (future)
    push_enabled = Column(Boolean, default=False)  # For push notifications (future)
    
    # Alert preferences
    notify_on_low = Column(Boolean, default=False)
    notify_on_medium = Column(Boolean, default=True)
    notify_on_high = Column(Boolean, default=True)
    notify_on_critical = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<UserSubscription(id={self.id}, user_id={self.user_id}, location={self.location})>"

