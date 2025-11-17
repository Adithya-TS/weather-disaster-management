#!/usr/bin/env python3
"""
Quick Test Script for ADK-Compliant Implementation
Tests basic functionality without requiring API keys
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from agents.multi_agent_system import (
            weather_data_agent,
            social_media_agent,
            disaster_analyzer_agent,
            response_planner_agent,
            verification_agent,
            alert_agent,
            root_disaster_management_agent
        )
        print("✓ Agents imported successfully")
        
        from tools.custom_tools import (
            get_weather_data,
            get_social_media_reports,
            analyze_disaster_type,
            generate_response_plan,
            send_emergency_alerts,
            verify_with_human
        )
        print("✓ Tools imported successfully")
        
        from observability.monitoring import ObservabilityManager, configure_logging
        print("✓ Observability imported successfully")
        
        from memory.session_memory import StateManager, InMemorySessionService
        print("✓ Memory management imported successfully")
        
        from main import WorkflowExecutor
        print("✓ Main executor imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_agent_structure():
    """Test agent structure and configuration."""
    print("\nTesting agent structure...")
    
    try:
        from agents.multi_agent_system import root_disaster_management_agent
        from google.adk.agents import LlmAgent
        
        # Check if root agent is an LlmAgent instance
        assert isinstance(root_disaster_management_agent, LlmAgent), "Root agent is not LlmAgent"
        print("✓ Root agent is LlmAgent instance")
        
        # Check if root agent has sub-agents
        assert hasattr(root_disaster_management_agent, 'sub_agents'), "No sub_agents attribute"
        assert len(root_disaster_management_agent.sub_agents) == 4, f"Expected 4 sub-agents, got {len(root_disaster_management_agent.sub_agents)}"
        print(f"✓ Root agent has {len(root_disaster_management_agent.sub_agents)} sub-agents")
        
        # Check if tools are functions
        from tools.custom_tools import get_weather_data
        assert callable(get_weather_data), "get_weather_data is not callable"
        print("✓ Tools are callable functions")
        
        return True
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_tool_execution():
    """Test tool execution (without API calls)."""
    print("\nTesting tool execution...")
    
    try:
        from tools.custom_tools import (
            get_social_media_reports,
            analyze_disaster_type,
            generate_response_plan,
            verify_with_human
        )
        
        # Test social media reports (doesn't need API)
        result = get_social_media_reports("Miami")
        assert isinstance(result, str), "Social media reports should return string"
        assert "Miami" in result, "City name should be in result"
        print("✓ get_social_media_reports works")
        
        # Test analyze_disaster_type
        weather_data = "Temperature: 35.0°C\nWind Speed: 15.0 m/s"
        social_reports = "Heavy rain reported"
        result = analyze_disaster_type(weather_data, social_reports)
        assert isinstance(result, str), "Analysis should return string"
        assert "Disaster Analysis" in result, "Result should contain analysis header"
        print("✓ analyze_disaster_type works")
        
        # Test generate_response_plan
        result = generate_response_plan("Hurricane", "Critical", "Miami")
        assert isinstance(result, str), "Response plan should return string"
        assert "EMERGENCY RESPONSE PLAN" in result, "Should contain plan header"
        assert "Miami" in result.upper(), "Should contain city name"
        print("✓ generate_response_plan works")
        
        # Test verify_with_human
        result = verify_with_human("Test plan with Severity Level: High")
        assert isinstance(result, str), "Verification should return string"
        assert "APPROVED" in result or "REJECTED" in result, "Should show approval status"
        print("✓ verify_with_human works")
        
        return True
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_management():
    """Test session management."""
    print("\nTesting session management...")
    
    try:
        from google.adk.sessions import InMemorySessionService
        from memory.session_memory import StateManager
        
        # Create session service
        session_service = InMemorySessionService()
        print("✓ InMemorySessionService created")
        
        # Create state manager
        state_manager = StateManager(session_service)
        print("✓ StateManager created")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("ADK Implementation Verification Tests")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Agent Structure", test_agent_structure()))
    results.append(("Tool Execution", test_tool_execution()))
    results.append(("Session Management", test_session_management()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your ADK implementation is ready.")
        print("\nNext steps:")
        print("1. Set GOOGLE_API_KEY and OPENWEATHER_API_KEY")
        print("2. Run: python src/main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
