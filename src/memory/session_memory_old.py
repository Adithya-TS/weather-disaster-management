"""
Session and Memory Management
Demonstrates: InMemorySessionService, Memory Bank, Context Engineering
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import asyncio
import structlog

logger = structlog.get_logger()


class SessionState(BaseModel):
    """Session state model"""
    session_id: str
    user_id: str = "system"
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    state_data: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    
    class Config:
        arbitrary_types_allowed = True


class InMemorySessionService:
    """
    In-Memory Session Management
    Demonstrates session state management for agent workflows
    """
    
    def __init__(self, session_timeout: int = 3600):
        self.sessions: Dict[str, SessionState] = {}
        self.session_timeout = session_timeout  # seconds
        
    async def create_session(self, session_id: str, user_id: str = "system") -> SessionState:
        """Create a new session"""
        session = SessionState(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            state_data={},
            is_active=True
        )
        
        self.sessions[session_id] = session
        logger.info("session.created", session_id=session_id, user_id=user_id)
        
        return session
        
    async def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve session by ID"""
        session = self.sessions.get(session_id)
        
        if session:
            # Check if session expired
            if await self._is_expired(session):
                await self.end_session(session_id)
                return None
                
            # Update last accessed
            session.last_accessed = datetime.now()
            logger.debug("session.accessed", session_id=session_id)
            
        return session
        
    async def update_session_state(
        self,
        session_id: str,
        state_updates: Dict[str, Any]
    ) -> SessionState:
        """Update session state"""
        session = await self.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")
            
        session.state_data.update(state_updates)
        session.last_accessed = datetime.now()
        
        logger.info("session.updated", session_id=session_id, updates=len(state_updates))
        return session
        
    async def end_session(self, session_id: str) -> None:
        """End a session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            logger.info("session.ended", session_id=session_id)
            
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired = []
        
        for session_id, session in self.sessions.items():
            if await self._is_expired(session):
                expired.append(session_id)
                
        for session_id in expired:
            del self.sessions[session_id]
            
        logger.info("session.cleanup", expired_count=len(expired))
        return len(expired)
        
    async def _is_expired(self, session: SessionState) -> bool:
        """Check if session is expired"""
        age = (datetime.now() - session.last_accessed).total_seconds()
        return age > self.session_timeout or not session.is_active
        
    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        return sum(1 for s in self.sessions.values() if s.is_active)


class DisasterEvent(BaseModel):
    """Disaster event model for memory storage"""
    event_id: str
    city: str
    disaster_type: str
    severity: str
    weather_data: Dict[str, Any]
    response_plan: str
    outcome: Optional[str] = None
    human_approved: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class MemoryBank:
    """
    Long-term Memory Storage
    Stores historical disaster events for pattern recognition and learning
    """
    
    def __init__(self, max_events: int = 1000):
        self.events: List[DisasterEvent] = []
        self.max_events = max_events
        self.event_index: Dict[str, DisasterEvent] = {}
        
    async def store_event(self, event: DisasterEvent) -> None:
        """Store a disaster event"""
        self.events.append(event)
        self.event_index[event.event_id] = event
        
        # Implement circular buffer
        if len(self.events) > self.max_events:
            removed = self.events.pop(0)
            del self.event_index[removed.event_id]
            
        logger.info(
            "memory.event_stored",
            event_id=event.event_id,
            city=event.city,
            disaster_type=event.disaster_type,
            total_events=len(self.events)
        )
        
    async def get_event(self, event_id: str) -> Optional[DisasterEvent]:
        """Retrieve event by ID"""
        return self.event_index.get(event_id)
        
    async def query_events(
        self,
        city: Optional[str] = None,
        disaster_type: Optional[str] = None,
        severity: Optional[str] = None,
        days_back: int = 30
    ) -> List[DisasterEvent]:
        """Query events with filters"""
        cutoff = datetime.now() - timedelta(days=days_back)
        results = []
        
        for event in self.events:
            # Time filter
            if event.timestamp < cutoff:
                continue
                
            # City filter
            if city and event.city.lower() != city.lower():
                continue
                
            # Disaster type filter
            if disaster_type and disaster_type.lower() not in event.disaster_type.lower():
                continue
                
            # Severity filter
            if severity and event.severity.lower() != severity.lower():
                continue
                
            results.append(event)
            
        logger.info(
            "memory.query",
            filters={"city": city, "disaster_type": disaster_type, "severity": severity},
            results_count=len(results)
        )
        
        return results
        
    async def get_pattern_analysis(self, city: str, days_back: int = 90) -> Dict[str, Any]:
        """Analyze patterns for a city"""
        events = await self.query_events(city=city, days_back=days_back)
        
        if not events:
            return {
                "city": city,
                "total_events": 0,
                "patterns": []
            }
            
        # Count disaster types
        disaster_counts = {}
        severity_counts = {}
        
        for event in events:
            disaster_counts[event.disaster_type] = disaster_counts.get(event.disaster_type, 0) + 1
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
            
        return {
            "city": city,
            "total_events": len(events),
            "time_range_days": days_back,
            "disaster_types": disaster_counts,
            "severity_distribution": severity_counts,
            "most_common_disaster": max(disaster_counts, key=disaster_counts.get) if disaster_counts else None,
            "average_severity_score": self._calculate_severity_score(severity_counts)
        }
        
    def _calculate_severity_score(self, severity_counts: Dict[str, int]) -> float:
        """Calculate average severity score"""
        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        total_score = 0
        total_count = 0
        
        for severity, count in severity_counts.items():
            weight = severity_weights.get(severity.lower(), 1)
            total_score += weight * count
            total_count += count
            
        return total_score / total_count if total_count > 0 else 0
        
    async def export_to_json(self, filepath: str) -> None:
        """Export memory to JSON file"""
        data = [
            {
                "event_id": e.event_id,
                "city": e.city,
                "disaster_type": e.disaster_type,
                "severity": e.severity,
                "weather_data": e.weather_data,
                "response_plan": e.response_plan,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata
            }
            for e in self.events
        ]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info("memory.exported", filepath=filepath, event_count=len(data))
        
    async def import_from_json(self, filepath: str) -> int:
        """Import memory from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        for item in data:
            event = DisasterEvent(
                event_id=item["event_id"],
                city=item["city"],
                disaster_type=item["disaster_type"],
                severity=item["severity"],
                weather_data=item["weather_data"],
                response_plan=item["response_plan"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                metadata=item.get("metadata", {})
            )
            await self.store_event(event)
            
        logger.info("memory.imported", filepath=filepath, event_count=len(data))
        return len(data)


class ContextCompactor:
    """
    Context Engineering: Context Compaction
    Reduces context size while preserving important information
    """
    
    def __init__(self, max_context_tokens: int = 4000):
        self.max_context_tokens = max_context_tokens
        
    async def compact_disaster_history(
        self,
        events: List[DisasterEvent],
        focus_city: str
    ) -> str:
        """Compact disaster history into summarized context"""
        
        if not events:
            return f"No historical disaster data available for {focus_city}."
            
        # Prioritize recent and severe events
        sorted_events = sorted(
            events,
            key=lambda e: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(e.severity.lower(), 0),
                e.timestamp
            ),
            reverse=True
        )
        
        # Take top events
        top_events = sorted_events[:5]
        
        summary = f"Historical Context for {focus_city}:\n\n"
        
        for i, event in enumerate(top_events, 1):
            summary += f"{i}. {event.disaster_type} ({event.severity}) - "
            summary += f"{event.timestamp.strftime('%Y-%m-%d')}\n"
            summary += f"   Temp: {event.weather_data.get('temperature')}°C, "
            summary += f"Wind: {event.weather_data.get('wind_speed')} m/s\n"
            
        # Add pattern summary
        disaster_types = [e.disaster_type for e in events]
        most_common = max(set(disaster_types), key=disaster_types.count)
        summary += f"\nMost common threat: {most_common} ({disaster_types.count(most_common)} occurrences)\n"
        
        logger.info(
            "context.compacted",
            city=focus_city,
            original_events=len(events),
            compacted_events=len(top_events)
        )
        
        return summary
        
    async def compact_weather_data(self, weather_data: Dict[str, Any]) -> str:
        """Compact weather data to essential information"""
        essential_fields = ["temperature", "wind_speed", "humidity", "pressure", "weather"]
        
        compact = []
        for field in essential_fields:
            if field in weather_data and weather_data[field] != "N/A":
                compact.append(f"{field}: {weather_data[field]}")
                
        return " | ".join(compact)


class StateManager:
    """
    Unified State Management
    Combines session and memory management
    """
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.memory_bank = MemoryBank()
        self.context_compactor = ContextCompactor()
        
    async def create_workflow_session(self, workflow_id: str, city: str) -> SessionState:
        """Create session for a workflow"""
        session = await self.session_service.create_session(
            session_id=workflow_id,
            user_id="disaster_management_system"
        )
        
        # Initialize with historical context
        historical_events = await self.memory_bank.query_events(city=city, days_back=30)
        context = await self.context_compactor.compact_disaster_history(historical_events, city)
        
        await self.session_service.update_session_state(
            session_id=workflow_id,
            state_updates={
                "city": city,
                "historical_context": context,
                "start_time": datetime.now().isoformat()
            }
        )
        
        return session
        
    async def save_workflow_result(
        self,
        session_id: str,
        event: DisasterEvent
    ) -> None:
        """Save workflow result to memory"""
        # Store in memory bank
        await self.memory_bank.store_event(event)
        
        # Update session
        await self.session_service.update_session_state(
            session_id=session_id,
            state_updates={
                "completed": True,
                "event_id": event.event_id,
                "end_time": datetime.now().isoformat()
            }
        )
        
        logger.info(
            "state_manager.result_saved",
            session_id=session_id,
            event_id=event.event_id
        )
