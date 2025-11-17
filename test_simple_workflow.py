"""
Simple test to verify the complete workflow works
"""

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
import os

from src.agents.multi_agent_system import root_disaster_management_agent
from src.observability.monitoring import ObservabilityManager

load_dotenv()


async def test_workflow():
    """Test the complete disaster management workflow."""
    
    # Setup
    observability = ObservabilityManager(log_level="INFO")
    session_service = InMemorySessionService()
    
    runner = Runner(
        agent=root_disaster_management_agent,
        app_name="disaster_test",
        session_service=session_service,
        plugins=[observability.get_plugin()]
    )
    
    # Create session
    session = await session_service.create_session(
        app_name="disaster_test",
        user_id="test_user",
        session_id="test_session_001"
    )
    
    # Create message
    user_message = types.Content(
        parts=[types.Part(
            text="Analyze disaster situation in Miami. Check weather, social media, analyze the disaster, create response plan, get verification, and send alerts. Complete ALL steps."
        )]
    )
    
    print("\n" + "="*70)
    print("TESTING COMPLETE DISASTER MANAGEMENT WORKFLOW")
    print("="*70 + "\n")
    
    # Execute
    full_response = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session_001",
        new_message=user_message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        full_response += part.text
    
    print("\n" + "="*70)
    print("FINAL RESPONSE:")
    print("="*70)
    print(full_response if full_response else "(No response text)")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_workflow())
