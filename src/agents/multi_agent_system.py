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
    validate_social_media_reports,
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
    description="Monitors social media for disaster-related reports and validates them against official weather data",
    instruction="""
    You collect and validate social media reports. When called:
    1. Use get_social_media_reports tool for the city to get reports
    2. Use validate_social_media_reports tool with the location and reports to fact-check them
    3. Summarize key findings and highlight any misinformation detected
    
    You are a sub-agent - just provide the validated reports, don't end the conversation.
    """,
    tools=[get_social_media_reports, validate_social_media_reports]
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
    You are a disaster analysis expert. Your task is to analyze weather and social media data to identify disaster type and severity.
    
    Follow these steps in order:
    1. Use the get_weather_data tool to fetch current weather conditions for the location
    2. Use the get_social_media_reports tool to gather citizen reports and social media signals
    3. Use the analyze_disaster_type tool with both the weather data and social media reports
    4. Provide a clear text summary that includes:
       - The identified disaster type (Hurricane, Flood, Tornado, Heatwave, Wildfire, etc.)
       - The severity level (Critical, High, Medium, Low)
       - Your reasoning based on the collected data
    
    IMPORTANT:
    - Use the available tools (get_weather_data, get_social_media_reports, analyze_disaster_type)
    - DO NOT write Python code or use print() statements
    - DO NOT try to execute code - just use the tools provided
    - Always end with a clear summary sentence about the disaster situation
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
    You are a disaster management coordinator. Your job is to orchestrate the complete workflow.
    
    You have access to 4 specialized sub-agents that will be automatically called for you:
    1. disaster_analyzer_agent - Analyzes weather and social media to identify disaster type and severity
    2. response_planner_agent - Creates comprehensive response plans
    3. verification_agent - Handles human verification and approval
    4. alert_agent - Distributes emergency alerts
    
    Workflow steps:
    1. First, delegate the disaster analysis task. The disaster_analyzer_agent will automatically be called.
    2. Once you receive the analysis results (disaster type and severity), delegate response planning to response_planner_agent.
    3. After receiving the response plan, delegate verification to verification_agent.
    4. Once verified, delegate alert distribution to alert_agent.
    5. Finally, provide a comprehensive summary of the entire workflow.
    
    IMPORTANT:
    - DO NOT write code or try to call functions like transfer_to_agent()
    - DO NOT use print() statements or execute Python code
    - Simply describe what needs to be done and the sub-agents will be automatically invoked
    - Wait for each agent to complete before moving to the next step
    - Complete ALL steps before ending your response
    
    When delegating, clearly state what information you need from each agent.
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
