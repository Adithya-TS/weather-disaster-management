"""Notification log model to track sent notifications."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..database.connection import Base


class NotificationType(enum.Enum):
    """Types of notifications."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(enum.Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class NotificationLog(Base):
    """Model for tracking sent notifications."""
    
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification details
    notification_type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    
    # Recipient info
    recipient_email = Column(String(255))
    recipient_phone = Column(String(20))
    
    # Content
    subject = Column(String(255))
    message = Column(Text)
    
    # Delivery info
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    alert = relationship("Alert")
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, user_id={self.user_id}, type={self.notification_type.value}, status={self.status.value})>"

