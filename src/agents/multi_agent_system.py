"""
Multi-Agent System Implementation using Google ADK
Demonstrates: Sequential agents, Parallel agents, Sub-agents using ADK framework

Following the Google ADK template pattern from Kaggle 5-day Agents course.
"""

from typing import Dict, Any, List
import structlog

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

logger = structlog.get_logger()

# Configure retry options for LLM calls (matches ADK template pattern)
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


# Import tools from custom_tools module
from ..tools.custom_tools import (
    get_weather_data,
    get_social_media_reports,
    analyze_disaster_type,
    generate_response_plan,
    send_emergency_alerts,
    verify_with_human,
)


# Weather Data Agent
weather_data_agent = LlmAgent(
    name="weather_data_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Collects real-time weather data from OpenWeatherMap API",
    instruction="""
    You collect weather data. When called:
    1. Use get_weather_data tool for the city
    2. Format the data clearly
    
    You are a sub-agent - just provide the data, don't end the conversation.
    """,
    tools=[get_weather_data]
)

# Social Media Monitoring Agent
social_media_agent = LlmAgent(
    name="social_media_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Monitors social media for disaster-related reports",
    instruction="""
    You collect social media reports. When called:
    1. Use get_social_media_reports tool for the city
    2. Summarize key findings
    
    You are a sub-agent - just provide the reports, don't end the conversation.
    """,
    tools=[get_social_media_reports]
)

# Disaster Analysis Agent
disaster_analyzer_agent = LlmAgent(
    name="disaster_analyzer_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
        generation_config={"temperature": 0.3}  # Slightly higher for text generation
    ),
    description="Analyzes weather data and social media to identify disaster type and severity",
    instruction="""
    Execute ALL steps:
    1. Call get_weather_data
    2. Call get_social_media_reports
    3. Call analyze_disaster_type with the weather and social data
    4. YOU MUST write a text summary explaining the disaster type, severity, and reasoning
    
    Always end with a summary sentence about the disaster situation.
    """,
    tools=[get_weather_data, get_social_media_reports, analyze_disaster_type]
)

# Response Planning Agent
response_planner_agent = LlmAgent(
    name="response_planner_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Generates comprehensive disaster response plans",
    instruction="""
    You are an emergency response planning specialist.
    
    1. Use generate_response_plan tool with disaster type, severity, and city from the analysis
    2. Present the comprehensive response plan
    3. Return to coordinator to continue the workflow (DO NOT end here)
    
    Create actionable, specific, time-sensitive plans.
    """,
    tools=[generate_response_plan]
)

# Verification Agent
verification_agent = LlmAgent(
    name="verification_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Manages human-in-the-loop verification",
    instruction="""
    You are a verification coordinator.
    
    1. Use verify_with_human tool to get approval for the response plan
    2. Report the verification status (approved/rejected)
    3. Return to coordinator to continue (DO NOT end the workflow)
    """,
    tools=[verify_with_human]
)

# Alert Agent
alert_agent = LlmAgent(
    name="alert_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Distributes emergency alerts",
    instruction="""
    You are an emergency alert distribution specialist.
    
    1. Use send_emergency_alerts tool with the approved response plan
    2. Confirm successful distribution across all channels
    3. Return final confirmation to coordinator
    
    This is the FINAL step - after alerts are sent, workflow is complete.
    """,
    tools=[send_emergency_alerts]
)

# Root Agent - Orchestrates entire workflow
root_disaster_management_agent = LlmAgent(
    name="disaster_management_coordinator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Coordinates complete disaster management workflow",
    instruction="""
    You coordinate disaster management. Execute ALL steps IN ORDER:
    
    1. Transfer to disaster_analyzer_agent - get disaster analysis
    2. Wait for analysis, then transfer to response_planner_agent - get response plan  
    3. Wait for plan, then transfer to verification_agent - get approval
    4. Wait for approval, then transfer to alert_agent - send alerts
    5. After all steps complete, provide final summary
    
    DO NOT stop until ALL 4 agents have completed their tasks.
    Each agent will return their results - use those results for the next agent.
    Complete the ENTIRE workflow before ending.
    """,
    sub_agents=[disaster_analyzer_agent, response_planner_agent, verification_agent, alert_agent]
)


# Compatibility classes
class AgentState:
    def __init__(self, city: str):
        self.city = city
        self.weather_data: Dict[str, Any] = {}
        self.social_media_reports: List[str] = []
        self.disaster_type: str = ""
        self.severity: str = ""
        self.response_plan: str = ""
        self.human_approved: bool = False
        self.alerts_sent: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}


class ParallelDataCollectorAgent:
    def __init__(self):
        self.weather_agent = weather_data_agent
        self.social_agent = social_media_agent


class SequentialWorkflowAgent:
    def __init__(self):
        self.root_agent = root_disaster_management_agent


class HumanVerificationAgent:
    def __init__(self):
        self.verification_agent = verification_agent
