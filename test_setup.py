#!/usr/bin/env python
"""
Test script to verify the environment setup
"""

print("🔍 Testing Google ADK Installation...")
print("=" * 60)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.sessions import InMemorySessionService
    from google.adk.plugins.logging_plugin import LoggingPlugin
    print("   ✅ Google ADK core imports successful")
except ImportError as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 2: Additional dependencies
print("\n2. Testing additional dependencies...")
try:
    import structlog
    import requests
    import pydantic
    print("   ✅ Additional dependencies imported successfully")
except ImportError as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 3: Project agents
print("\n3. Testing project agents...")
try:
    from src.agents.multi_agent_system import root_disaster_management_agent
    print(f"   ✅ Root agent imported: {root_disaster_management_agent.name}")
except ImportError as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 4: Project tools
print("\n4. Testing project tools...")
try:
    from src.tools.custom_tools import get_weather_data, analyze_disaster_type
    print("   ✅ Tools imported successfully")
except ImportError as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 5: Observability
print("\n5. Testing observability modules...")
try:
    from src.observability.monitoring import ObservabilityManager
    print("   ✅ Observability modules imported successfully")
except ImportError as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 6: Session management
print("\n6. Testing session management...")
try:
    from src.memory.session_memory import StateManager
    print("   ✅ Session management imported successfully")
except ImportError as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\n✅ Your environment is correctly set up!")
print("✅ All dependencies are installed")
print("✅ All modules can be imported")
print("\nYou're ready to run the weather disaster management system!")
