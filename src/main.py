"""
Main Workflow Executor using Google ADK
Demonstrates: Runner, Session Management, Plugins, Complete Workflow
"""

import asyncio
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv
import structlog

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents.multi_agent_system import root_disaster_management_agent
from .observability.monitoring import ObservabilityManager
from .memory.session_memory import StateManager, DisasterEvent

# Load environment variables
load_dotenv()

logger = structlog.get_logger()


def format_disaster_response(raw_response: str, location_name: str) -> str:
    """
    Format the agent's disaster analysis response for better readability.
    
    Args:
        raw_response: Raw response from the agent
        location_name: Full location name with city, state, country
        
    Returns:
        Formatted response string
    """
    if not raw_response or not raw_response.strip():
        return f"Analysis completed for {location_name}. No immediate disaster threats detected."
    
    # Clean up the response
    response = raw_response.strip()
    
    # Add header if not present
    if not response.startswith("DISASTER ANALYSIS") and not response.startswith("Weather Disaster"):
        response = f"WEATHER DISASTER ANALYSIS - {location_name.upper()}\n{'='*70}\n\n{response}"
    
    # Add footer with timestamp
    if not "analyzed at" in response.lower() and not "timestamp" in response.lower():
        from datetime import datetime
        response += f"\n\n{'='*70}\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return response


class WorkflowExecutor:
    """
    Main workflow executor using Google ADK.
    Coordinates disaster management using ADK Runner and agents.
    """
    
    def __init__(self):
        """Initialize the workflow executor with ADK components."""
        # Initialize observability (includes LoggingPlugin)
        self.observability = ObservabilityManager(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_dir="logs"
        )
        
        # Initialize session service (ADK's InMemorySessionService)
        self.session_service = InMemorySessionService()
        
        # Initialize state manager
        self.state_manager = StateManager(self.session_service)
        
        # Application configuration
        self.app_name = "disaster_management"
        self.user_id = "system"
        
        # Initialize ADK Runner with root agent and plugins
        self.runner = Runner(
            agent=root_disaster_management_agent,
            app_name=self.app_name,
            session_service=self.session_service,
            plugins=[self.observability.get_plugin()]  # Add LoggingPlugin
        )
        
        logger.info("workflow_executor.initialized", 
                   app_name=self.app_name,
                   log_file=self.observability.get_log_file())
    
    async def execute(self, location: str) -> dict:
        """
        Execute the complete disaster management workflow for a location.
        
        Args:
            location: Location (area, city, village) to analyze
            
        Returns:
            dict: Workflow results including disaster analysis and actions taken
        """
        # Generate unique session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Log workflow start
        start_time = datetime.now()
        self.observability.log_workflow_start(location=location, session_id=session_id)
        
        try:
            # Create session
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id
            )
            
            # Create user message
            user_message = types.Content(
                parts=[types.Part(
                    text=f"Analyze and respond to weather disaster situation in {location}"
                )]
            )
            
            # Execute agent workflow using Runner
            logger.info("workflow.executing_agent", location=location, session_id=session_id)
            
            response_text = ""
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=session_id,
                new_message=user_message
            ):
                # Collect final response
                if event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                response_text += part.text
                    elif not event.content:
                        logger.warning("final_response_no_content", event_id=str(event))
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log the final agent response
            if response_text:
                logger.info("agent_response.final",
                           location=location,
                           session_id=session_id,
                           response=response_text,
                           response_length=len(response_text))
            
            # Log success
            self.observability.log_workflow_complete(
                location=location,
                duration=duration,
                session_id=session_id
            )
            
            # Try to get detailed location info from weather data if available
            location_info = {"location": location}
            try:
                from .tools.custom_tools import geocode_location
                geo_data = geocode_location(location)
                logger.info("workflow.geocode_attempt", location=location, geo_data=geo_data)
                if geo_data:
                    location_parts = [geo_data.get("name", location)]
                    if geo_data.get("state"):
                        location_parts.append(geo_data["state"])
                    if geo_data.get("country"):
                        location_parts.append(geo_data["country"])
                    location_info = {
                        "location": location,
                        "city": geo_data.get("name", location),
                        "state": geo_data.get("state", ""),
                        "country": geo_data.get("country", ""),
                        "full_location": ", ".join(location_parts)
                    }
                    logger.info("workflow.location_info_created", location_info=location_info)
            except Exception as e:
                logger.warning("workflow.geocode_failed", error=str(e), location=location)
            
            # Format the response for better presentation
            formatted_response = format_disaster_response(
                response_text, 
                location_info.get("full_location", location)
            )
            
            return {
                "success": True,
                **location_info,
                "session_id": session_id,
                "response": formatted_response,
                "raw_response": response_text,  # Keep original for reference
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Log error
            error_msg = str(e)
            self.observability.log_workflow_error(location=location, error=error_msg)
            
            return {
                "success": False,
                "location": location,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }


async def main():
    """Main entry point for the application."""
    # Create executor
    executor = WorkflowExecutor()
    
    # Example: Execute for a city
    city = os.getenv("DEMO_CITY", "Miami")
    print(f"\n{'='*60}")
    print(f"Disaster Management System - Analyzing {city}")
    print(f"Log File: {executor.observability.get_log_file()}")
    print(f"{'='*60}\n")
    
    result = await executor.execute(city)
    
    print(f"\n{'='*60}")
    print("RESULTS:")
    print(f"{'='*60}")
    print(f"Success: {result['success']}")
    print(f"City: {result['city']}")
    if result['success']:
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"\nAgent Response:\n{result['response']}")
    else:
        print(f"Error: {result.get('error')}")
    print(f"\n📝 Full logs saved to: {executor.observability.get_log_file()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
