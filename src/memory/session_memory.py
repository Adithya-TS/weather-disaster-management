"""
Session and Memory Management using ADK
Demonstrates: InMemorySessionService from Google ADK
"""

from typing import Dict, Any
from datetime import datetime
import structlog

from google.adk.sessions import InMemorySessionService as ADKSessionService

logger = structlog.get_logger()


# Re-export ADK's InMemorySessionService for backward compatibility
InMemorySessionService = ADKSessionService


class StateManager:
    """
    State manager for disaster management workflows.
    Uses ADK's session service internally.
    """
    
    def __init__(self, session_service: ADKSessionService = None):
        """
        Initialize state manager.
        
        Args:
            session_service: ADK session service instance (optional)
        """
        self.session_service = session_service or ADKSessionService()
        self.logger = structlog.get_logger("state_manager")
        self.logger.info("state_manager.initialized")
    
    async def get_session(self, app_name: str, user_id: str, session_id: str):
        """Get or create a session."""
        try:
            session = await self.session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            if not session:
                session = await self.session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
            return session
        except Exception as e:
            self.logger.error("state_manager.get_session_error", error=str(e))
            raise
    
    async def update_state(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        updates: Dict[str, Any]
    ):
        """Update session state."""
        try:
            await self.session_service.add_session_messages(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                new_messages=updates.get("messages", [])
            )
            self.logger.info("state_manager.state_updated", session_id=session_id)
        except Exception as e:
            self.logger.error("state_manager.update_state_error", error=str(e))
            raise


class DisasterEvent:
    """
    Represents a disaster event in the system.
    Simple data class for disaster tracking.
    """
    
    def __init__(
        self,
        city: str,
        disaster_type: str = "",
        severity: str = "",
        timestamp: datetime = None
    ):
        self.city = city
        self.disaster_type = disaster_type
        self.severity = severity
        self.timestamp = timestamp or datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "city": self.city,
            "disaster_type": self.disaster_type,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
