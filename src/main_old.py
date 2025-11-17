"""
Main Workflow Executor
Orchestrates the complete multi-agent disaster management system
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
import structlog

from agents.multi_agent_system import (
    ParallelDataCollectorAgent,
    SequentialWorkflowAgent,
    HumanVerificationAgent,
    AgentState
)
from tools.custom_tools import ToolRegistry, EmailAlertTool, DataLoggingTool
from tools.mcp_integration import MCPRegistry
from memory.session_memory import StateManager, DisasterEvent
from observability.monitoring import ObservabilityManager, configure_logging
from evaluation.agent_evaluation import EvaluationSuite

# Load environment variables
load_dotenv()

# Configure logging
configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_format=os.getenv("LOG_FORMAT", "json")
)

logger = structlog.get_logger()


class WorkflowExecutor:
    """
    Main workflow executor
    Coordinates all agents and manages the complete disaster management flow
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
        # Initialize components
        self.tools = ToolRegistry()
        self.mcp = MCPRegistry()
        self.state_manager = StateManager()
        self.observability = ObservabilityManager()
        
        # Initialize agents
        self.data_collector = ParallelDataCollectorAgent()
        self.sequential_workflow = SequentialWorkflowAgent(llm_client)
        self.verifier = HumanVerificationAgent()
        
        logger.info("workflow_executor.initialized")
        
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute complete disaster management workflow
        Demonstrates end-to-end multi-agent coordination
        """
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        trace_id = workflow_id
        
        logger.info(
            "workflow.start",
            workflow_id=workflow_id,
            city=state.city
        )
        
        # Start tracing
        with self.observability.tracer.trace_context(
            trace_id=trace_id,
            operation="disaster_management_workflow",
            city=state.city
        ):
            # Create session
            session = await self.state_manager.create_workflow_session(
                workflow_id=workflow_id,
                city=state.city
            )
            
            try:
                # Step 1: Parallel data collection
                logger.info("workflow.step", step="data_collection", city=state.city)
                with self.observability.observe_agent_execution(
                    trace_id=trace_id,
                    agent_name="ParallelDataCollector",
                    operation="collect_data"
                ):
                    state = await self.data_collector.execute(state)
                    
                # Step 2: Sequential analysis and response generation
                logger.info("workflow.step", step="analysis", city=state.city)
                with self.observability.observe_agent_execution(
                    trace_id=trace_id,
                    agent_name="SequentialWorkflow",
                    operation="analyze_and_respond"
                ):
                    state = await self.sequential_workflow.execute(state)
                    
                # Log data
                logger.info("workflow.step", step="data_logging", city=state.city)
                data_logger = self.tools.get_tool("data_logger")
                await data_logger.execute({
                    "city": state.city,
                    "disaster_type": state.disaster_type,
                    "severity": state.severity,
                    "weather_data": state.weather_data,
                    "response_plan": state.response_plan,
                    "social_media_reports": state.social_media_reports
                })
                
                # Step 3: Human verification (for low/medium severity)
                logger.info("workflow.step", step="verification", city=state.city)
                with self.observability.observe_agent_execution(
                    trace_id=trace_id,
                    agent_name="HumanVerifier",
                    operation="verify_alert"
                ):
                    state = await self.verifier.execute(state)
                    
                # Step 4: Send alerts if approved
                if state.human_approved:
                    logger.info("workflow.step", step="send_alert", city=state.city)
                    await self._send_alerts(state, trace_id)
                    
                    # Record metrics
                    self.observability.metrics.record_alert_sent(
                        city=state.city,
                        severity=state.severity
                    )
                else:
                    logger.info("workflow.alert_rejected", city=state.city)
                    
                # Record disaster detection
                self.observability.metrics.record_disaster_detection(
                    city=state.city,
                    disaster_type=state.disaster_type,
                    severity=state.severity
                )
                
                # Save to memory
                event = DisasterEvent(
                    event_id=workflow_id,
                    city=state.city,
                    disaster_type=state.disaster_type,
                    severity=state.severity,
                    weather_data=state.weather_data,
                    response_plan=state.response_plan,
                    human_approved=state.human_approved
                )
                await self.state_manager.save_workflow_result(
                    session_id=workflow_id,
                    event=event
                )
                
                logger.info(
                    "workflow.complete",
                    workflow_id=workflow_id,
                    city=state.city,
                    disaster_type=state.disaster_type,
                    severity=state.severity,
                    alert_sent=state.human_approved
                )
                
                return state
                
            except Exception as e:
                logger.error(
                    "workflow.error",
                    workflow_id=workflow_id,
                    city=state.city,
                    error=str(e)
                )
                raise
                
    async def _send_alerts(self, state: AgentState, trace_id: str):
        """Send alerts through multiple channels"""
        
        # Email alert
        with self.observability.observe_tool_call(trace_id, "email_alert"):
            email_tool = self.tools.get_tool("email_alert")
            recipient = os.getenv("RECEIVER_EMAIL")
            
            subject = f"Weather Alert: {state.severity} severity in {state.city}"
            body = self._format_alert_body(state)
            
            await email_tool.execute(
                recipient=recipient,
                subject=subject,
                body=body,
                severity=state.severity
            )
            
        # MCP multi-channel notification
        mcp_notification = self.mcp.get_service("notification")
        await mcp_notification.send_alert(
            message=body,
            severity=state.severity,
            recipients=[recipient],
            channels=["email"]
        )
        
    def _format_alert_body(self, state: AgentState) -> str:
        """Format alert message body"""
        weather = state.weather_data
        
        body = f"""
Weather Alert for {state.city}

Disaster Type: {state.disaster_type}
Severity Level: {state.severity}

Current Weather Conditions:
- Description: {weather.get('weather', 'N/A')}
- Temperature: {weather.get('temperature', 'N/A')}°C
- Wind Speed: {weather.get('wind_speed', 'N/A')} m/s
- Humidity: {weather.get('humidity', 'N/A')}%
- Pressure: {weather.get('pressure', 'N/A')} hPa

Social Media Reports:
{chr(10).join(f"- {report}" for report in state.social_media_reports) if state.social_media_reports else "None"}

Response Plan:
{state.response_plan}

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if state.severity.lower() in ["low", "medium"]:
            body += "\nNote: This alert has been reviewed and approved by a human operator."
            
        return body


class ContinuousMonitor:
    """
    Continuous monitoring service
    Demonstrates loop agent pattern for scheduled monitoring
    """
    
    def __init__(self, executor: WorkflowExecutor, cities: List[str], interval: int = 3600):
        self.executor = executor
        self.cities = cities
        self.interval = interval  # seconds
        self.is_running = False
        
    async def start(self):
        """Start continuous monitoring"""
        self.is_running = True
        logger.info(
            "monitor.started",
            cities=self.cities,
            interval_seconds=self.interval
        )
        
        while self.is_running:
            for city in self.cities:
                try:
                    logger.info("monitor.check_city", city=city)
                    
                    state = AgentState(city=city)
                    await self.executor.execute(state)
                    
                except Exception as e:
                    logger.error("monitor.error", city=city, error=str(e))
                    
                # Brief delay between cities
                await asyncio.sleep(5)
                
            # Wait for next interval
            logger.info("monitor.interval_complete", next_check_in=self.interval)
            await asyncio.sleep(self.interval)
            
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("monitor.stopped")


async def run_single_check(city: str):
    """Run a single city check"""
    executor = WorkflowExecutor()
    state = AgentState(city=city)
    result = await executor.execute(state)
    
    print(f"\n{'='*60}")
    print(f"Weather Check Complete for {city}")
    print(f"{'='*60}")
    print(f"Disaster Type: {result.disaster_type}")
    print(f"Severity: {result.severity}")
    print(f"Alert Sent: {result.human_approved}")
    print(f"{'='*60}\n")
    
    return result


async def run_continuous_monitoring(cities: Optional[List[str]] = None, interval: int = 3600):
    """Run continuous monitoring"""
    if not cities:
        cities_str = os.getenv("CITIES", "London,Karachi")
        cities = [city.strip() for city in cities_str.split(",")]
        
    executor = WorkflowExecutor()
    monitor = ContinuousMonitor(executor, cities, interval)
    
    print(f"\nStarting continuous monitoring for cities: {', '.join(cities)}")
    print(f"Check interval: {interval} seconds\n")
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        monitor.stop()


async def run_evaluation():
    """Run agent evaluation"""
    print("\nRunning Agent Evaluation Suite...\n")
    
    executor = WorkflowExecutor()
    evaluation_suite = EvaluationSuite()
    
    results = await evaluation_suite.run_full_evaluation(executor)
    
    print(f"\n{'='*60}")
    print("Evaluation Results")
    print(f"{'='*60}")
    print(f"Detection Accuracy: {results['detection_accuracy']:.2%}")
    print(f"Tests Passed: {results['test_cases_passed']}/{results['test_cases_total']}")
    print(f"Average Execution Time: {results['average_execution_time']:.2f}s")
    print(f"Throughput: {results['throughput']:.2f} requests/second")
    print(f"{'='*60}\n")
    
    # Save detailed results
    import json
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Detailed results saved to evaluation_results.json\n")
    
    return results


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Weather Disaster Management System")
    parser.add_argument("--city", type=str, help="City to check")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=3600, help="Monitoring interval (seconds)")
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation suite")
    
    args = parser.parse_args()
    
    if args.evaluate:
        await run_evaluation()
    elif args.city:
        await run_single_check(args.city)
    elif args.monitor:
        await run_continuous_monitoring(interval=args.interval)
    else:
        # Default: run single check for a test city
        await run_single_check("London")


if __name__ == "__main__":
    asyncio.run(main())
