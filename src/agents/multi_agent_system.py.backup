"""
Multi-Agent System Implementation
Demonstrates: Sequential agents, Parallel agents, Loop agents using Google ADK
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field
import structlog

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from ..tools.custom_tools import (
    get_weather_data,
    get_social_media_reports,
    analyze_disaster_type,
    generate_response_plan,
    send_emergency_alerts
)

logger = structlog.get_logger()

# Configure retry options for LLM calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)



class AgentRole(Enum):
    """Agent role definitions"""
    DATA_COLLECTOR = "data_collector"
    ANALYZER = "analyzer"
    RESPONDER = "responder"
    VERIFIER = "verifier"
    MONITOR = "monitor"


class AgentState(BaseModel):
    """Shared state between agents"""
    city: str
    weather_data: Dict[str, Any] = Field(default_factory=dict)
    social_media_reports: List[str] = Field(default_factory=list)
    disaster_type: str = ""
    severity: str = ""
    response_plan: str = ""
    human_approved: bool = False
    alerts_sent: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


# Weather Data Collection Agent - using ADK LlmAgent
weather_data_agent = LlmAgent(
    name="weather_data_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Collects real-time weather data from OpenWeatherMap API",
    instruction="""
    You are a weather data collection specialist.
    Use the get_weather_data tool to fetch current weather conditions for the specified city.
    Return comprehensive weather information including temperature, wind speed, humidity, pressure, and cloud cover.
    """,
    tools=[get_weather_data]
)

# Social Media Monitoring Agent - using ADK LlmAgent
social_media_agent = LlmAgent(
    name="social_media_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Monitors social media for disaster-related reports and citizen alerts",
    instruction="""
    You are a social media monitoring specialist.
    Use the get_social_media_reports tool to collect citizen reports about weather conditions and potential disasters.
    Extract relevant information about weather threats, damage reports, and public safety concerns.
    """,
    tools=[get_social_media_reports]
)

# Disaster Analysis Agent - using ADK LlmAgent
disaster_analyzer_agent = LlmAgent(
    name="disaster_analyzer_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Analyzes weather data and social media to identify disaster type and severity",
    instruction="""
    You are a disaster analysis expert.
    
    Analyze the provided weather data and social media reports to:
    1. Identify the type of disaster (Hurricane, Flood, Tornado, Heatwave, Wildfire, etc.)
    2. Assess severity level (Critical, High, Medium, Low)
    3. Consider both meteorological data and citizen reports
    
    Use the analyze_disaster_type tool with the collected data.
    Provide clear reasoning for your assessment.
    """,
    tools=[analyze_disaster_type]
)

# Response Planning Agent - using ADK LlmAgent
response_planner_agent = LlmAgent(
    name="response_planner_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Generates comprehensive disaster response plans",
    instruction="""
    You are an emergency response planning specialist.
    
    Based on the disaster type and severity, generate a comprehensive response plan including:
    1. Immediate actions required
    2. Resource deployment recommendations
    3. Public safety measures
    4. Coordination with emergency services
    
    Use the generate_response_plan tool with the disaster analysis.
    Be specific and actionable in your recommendations.
    """,
    tools=[generate_response_plan]
)

# Alert Distribution Agent - using ADK LlmAgent
alert_agent = LlmAgent(
    name="alert_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Distributes emergency alerts to relevant authorities and public",
    instruction="""
    You are an emergency alert distribution specialist.
    
    Send alerts based on the response plan to:
    1. Emergency services (fire, police, medical)
    2. Public works and utilities
    3. Civil defense and disaster management
    4. General public through various channels
    
    Use the send_emergency_alerts tool with the approved response plan.
    Ensure alerts are clear, urgent, and actionable.
    """,
    tools=[send_emergency_alerts]
)


class ParallelDataCollectorAgent:
    """
    Orchestrator for parallel data collection
    Demonstrates parallel agent execution pattern
    """
    
    def __init__(self):
        self.weather_agent = weather_data_agent
        self.social_agent = social_media_agent

        
    async def execute(self, state: AgentState) -> AgentState:
        """Fetch weather data using custom tool"""
        self.log_execution(state, "start")
        
        weather_tool = self.tools.get_tool("weather_api")
        weather_data = await weather_tool.execute(state.city)
        
        if weather_data.success:
            state.weather_data = {
                "weather": weather_data.weather,
                "temperature": weather_data.temperature,
                "wind_speed": weather_data.wind_speed,
                "humidity": weather_data.humidity,
                "pressure": weather_data.pressure,
                "cloud_cover": weather_data.cloud_cover,
                "timestamp": weather_data.timestamp
            }
            self.log_execution(state, "success", temperature=weather_data.temperature)
        else:
            self.log_execution(state, "error", error=weather_data.error)
            
        return state


class SocialMediaAgent(BaseAgent):
    """
    Agent for monitoring social media
    Part of parallel data collection
    """
    
    def __init__(self):
        super().__init__(AgentRole.DATA_COLLECTOR, "SocialMediaAgent")
        
    async def execute(self, state: AgentState) -> AgentState:
        """Monitor social media using custom tool"""
        self.log_execution(state, "start")
        
        social_tool = self.tools.get_tool("social_media_monitor")
        reports = await social_tool.execute(state.city, state.disaster_type or "unknown")
        
        state.social_media_reports = reports
        self.log_execution(state, "success", report_count=len(reports))
        
        return state


class ParallelDataCollectorAgent(BaseAgent):
    """
    Parallel Agent: Coordinates parallel data collection
    Demonstrates parallel agent execution
    """
    
    def __init__(self):
        super().__init__(AgentRole.DATA_COLLECTOR, "ParallelDataCollectorAgent")
        self.weather_agent = WeatherDataAgent()
        self.social_agent = SocialMediaAgent()
        
    async def execute(self, state: AgentState) -> AgentState:
        """Execute weather and social media collection in parallel"""
        self.log_execution(state, "start_parallel")
        
        # Execute both agents in parallel
        start_time = datetime.now()
        
        weather_task = self.weather_agent.execute(state)
        social_task = self.social_agent.execute(state)
        
        # Wait for both to complete
        state, _ = await asyncio.gather(weather_task, social_task)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        self.log_execution(state, "complete_parallel", elapsed_seconds=elapsed)
        
        return state


class DisasterAnalysisAgent(BaseAgent):
    """
    Sequential Agent: Analyzes disaster type
    Part of sequential processing pipeline
    """
    
    def __init__(self, llm_client):
        super().__init__(AgentRole.ANALYZER, "DisasterAnalysisAgent")
        self.llm = llm_client
        
    async def execute(self, state: AgentState) -> AgentState:
        """Analyze weather data to identify disaster type"""
        self.log_execution(state, "start")
        
        # Build prompt for LLM
        prompt = self._build_analysis_prompt(state)
        
        # Call LLM
        response = await self._call_llm(prompt)
        state.disaster_type = response.strip()
        
        # Enrich with MCP context
        mcp_weather = self.mcp.get_service("weather_context")
        context = await mcp_weather.get_weather_context(state.city)
        state.metadata["mcp_context"] = context
        
        self.log_execution(state, "complete", disaster_type=state.disaster_type)
        return state
        
    def _build_analysis_prompt(self, state: AgentState) -> str:
        """Build prompt for disaster analysis"""
        weather = state.weather_data
        social = "\n".join(state.social_media_reports) if state.social_media_reports else "None"
        
        return f"""Analyze the following weather conditions and identify potential disaster type:

Weather Conditions:
- Description: {weather.get('weather', 'N/A')}
- Temperature: {weather.get('temperature', 'N/A')}°C
- Wind Speed: {weather.get('wind_speed', 'N/A')} m/s
- Humidity: {weather.get('humidity', 'N/A')}%
- Pressure: {weather.get('pressure', 'N/A')} hPa

Social Media Reports:
{social}

Categorize into ONE of these types: Hurricane, Flood, Heatwave, Severe Storm, Winter Storm, or No Immediate Threat

Respond with ONLY the disaster type."""
        
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM for analysis"""
        # Simulate LLM call - in production would use actual Google Gemini
        await asyncio.sleep(0.5)
        
        # Simple rule-based logic for demonstration
        if "severe" in prompt.lower() or "storm" in prompt.lower():
            return "Severe Storm"
        elif "flood" in prompt.lower():
            return "Flood"
        elif "heat" in prompt.lower():
            return "Heatwave"
        else:
            return "No Immediate Threat"


class SeverityAssessmentAgent(BaseAgent):
    """
    Sequential Agent: Assesses severity level
    Part of sequential processing pipeline
    """
    
    def __init__(self, llm_client):
        super().__init__(AgentRole.ANALYZER, "SeverityAssessmentAgent")
        self.llm = llm_client
        
    async def execute(self, state: AgentState) -> AgentState:
        """Assess severity of the disaster"""
        self.log_execution(state, "start", disaster_type=state.disaster_type)
        
        prompt = self._build_severity_prompt(state)
        response = await self._call_llm(prompt)
        state.severity = response.strip()
        
        self.log_execution(state, "complete", severity=state.severity)
        return state
        
    def _build_severity_prompt(self, state: AgentState) -> str:
        """Build prompt for severity assessment"""
        weather = state.weather_data
        
        return f"""Assess the severity of this {state.disaster_type} disaster:

Weather Data:
- Temperature: {weather.get('temperature', 'N/A')}°C
- Wind Speed: {weather.get('wind_speed', 'N/A')} m/s
- Pressure: {weather.get('pressure', 'N/A')} hPa

Social Media Indicators: {len(state.social_media_reports)} reports

Respond with ONE of: Critical, High, Medium, or Low"""
        
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM for severity assessment"""
        await asyncio.sleep(0.3)
        
        # Rule-based logic for demonstration
        if "severe storm" in prompt.lower():
            return "High"
        elif "hurricane" in prompt.lower():
            return "Critical"
        elif "heatwave" in prompt.lower():
            return "Medium"
        else:
            return "Low"


class ResponseGeneratorAgent(BaseAgent):
    """
    Sequential Agent: Generates response plan
    Part of sequential processing pipeline
    """
    
    def __init__(self, llm_client):
        super().__init__(AgentRole.RESPONDER, "ResponseGeneratorAgent")
        self.llm = llm_client
        
    async def execute(self, state: AgentState) -> AgentState:
        """Generate disaster response plan"""
        self.log_execution(state, "start", severity=state.severity)
        
        # Get disaster research context
        research_tool = self.tools.get_tool("disaster_research")
        guidelines = await research_tool.execute(state.disaster_type, state.city)
        
        # Generate response plan
        prompt = self._build_response_prompt(state, guidelines)
        response = await self._call_llm(prompt)
        state.response_plan = response
        
        self.log_execution(state, "complete")
        return state
        
    def _build_response_prompt(self, state: AgentState, guidelines: Dict[str, Any]) -> str:
        """Build prompt for response generation"""
        return f"""Create an emergency response plan for {state.city}:

Disaster: {state.disaster_type}
Severity: {state.severity}

Guidelines:
Preparation: {guidelines.get('guidelines', {}).get('preparation', [])}
Response: {guidelines.get('guidelines', {}).get('response', [])}

Create a comprehensive but concise response plan."""
        
    async def _call_llm(self, prompt: str) -> str:
        """Generate response plan using LLM"""
        await asyncio.sleep(0.4)
        
        return f"""Emergency Response Plan:
1. Activate emergency services
2. Issue public warning
3. Prepare evacuation routes if needed
4. Monitor situation closely
5. Coordinate with local authorities"""


class HumanVerificationAgent(BaseAgent):
    """
    Long-Running Agent: Handles human verification with pause/resume
    Demonstrates long-running operations with human-in-the-loop
    """
    
    def __init__(self):
        super().__init__(AgentRole.VERIFIER, "HumanVerificationAgent")
        self.verification_timeout = 300  # 5 minutes
        
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute human verification with pause capability
        For low/medium severity, requires human approval
        """
        self.log_execution(state, "start", severity=state.severity)
        
        if state.severity.lower() in ["critical", "high"]:
            # Auto-approve high severity
            state.human_approved = True
            self.log_execution(state, "auto_approved")
        else:
            # Request human verification - this is a long-running operation
            state.human_approved = await self._request_human_verification(state)
            self.log_execution(
                state,
                "human_decision",
                approved=state.human_approved
            )
            
        return state
        
    async def _request_human_verification(self, state: AgentState) -> bool:
        """
        Request human verification
        In production, this would:
        1. Pause the agent workflow
        2. Send notification to operator
        3. Wait for human input
        4. Resume workflow with decision
        """
        print("\n" + "="*60)
        print(f"HUMAN VERIFICATION REQUIRED - {state.city}")
        print("="*60)
        print(f"Disaster Type: {state.disaster_type}")
        print(f"Severity: {state.severity}")
        print(f"Temperature: {state.weather_data.get('temperature')}°C")
        print(f"Wind Speed: {state.weather_data.get('wind_speed')} m/s")
        print(f"\nResponse Plan:\n{state.response_plan}")
        print("\n" + "="*60)
        print("Approve sending alert? (y/n): ", end='')
        
        # In production, this would use a proper pause/resume mechanism
        # For now, simulate with asyncio sleep + user input
        try:
            # Simulate waiting for input with timeout
            await asyncio.sleep(1)
            # For demonstration, auto-approve after delay
            decision = True  # In real implementation: get user input
            return decision
        except asyncio.TimeoutError:
            logger.warning("human_verification.timeout", city=state.city)
            return False


class SequentialWorkflowAgent(BaseAgent):
    """
    Sequential Agent Coordinator
    Orchestrates sequential agent execution
    """
    
    def __init__(self, llm_client):
        super().__init__(AgentRole.ANALYZER, "SequentialWorkflowAgent")
        self.agents = [
            DisasterAnalysisAgent(llm_client),
            SeverityAssessmentAgent(llm_client),
            ResponseGeneratorAgent(llm_client),
        ]
        
    async def execute(self, state: AgentState) -> AgentState:
        """Execute agents sequentially"""
        self.log_execution(state, "start_sequence", agent_count=len(self.agents))
        
        for agent in self.agents:
            state = await agent.execute(state)
            
        self.log_execution(state, "complete_sequence")
        return state


class ContinuousMonitorAgent(BaseAgent):
    """
    Loop Agent: Continuous monitoring
    Demonstrates loop agent pattern for scheduled checks
    """
    
    def __init__(self, cities: List[str], check_interval: int = 60):
        super().__init__(AgentRole.MONITOR, "ContinuousMonitorAgent")
        self.cities = cities
        self.check_interval = check_interval  # seconds
        self.is_running = False
        
    async def start_monitoring(self, workflow_executor):
        """Start continuous monitoring loop"""
        self.is_running = True
        logger.info("monitor_agent.started", cities=self.cities, interval=self.check_interval)
        
        while self.is_running:
            for city in self.cities:
                try:
                    await self._check_city(city, workflow_executor)
                except Exception as e:
                    logger.error("monitor_agent.error", city=city, error=str(e))
                    
            # Wait for next interval
            await asyncio.sleep(self.check_interval)
            
    async def _check_city(self, city: str, workflow_executor):
        """Check weather conditions for a city"""
        logger.info("monitor_agent.check", city=city)
        
        # Create initial state
        state = AgentState(city=city)
        
        # Execute complete workflow
        final_state = await workflow_executor.execute(state)
        
        logger.info(
            "monitor_agent.check_complete",
            city=city,
            disaster_type=final_state.disaster_type,
            severity=final_state.severity
        )
        
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("monitor_agent.stopped")
        
    async def execute(self, state: AgentState) -> AgentState:
        """Not used for loop agent"""
        return state
