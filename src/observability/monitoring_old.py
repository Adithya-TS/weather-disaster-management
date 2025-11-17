"""
Observability: Logging, Tracing, and Metrics
Demonstrates comprehensive monitoring and observability
"""

import structlog
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import time
from contextlib import contextmanager


# Configure structured logging
def configure_logging(log_level: str = "INFO", log_format: str = "json"):
    """Configure structured logging with structlog"""
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
        
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )


class EventLogger:
    """
    Structured event logging for agent actions
    """
    
    def __init__(self, component: str):
        self.logger = structlog.get_logger(component=component)
        self.component = component
        
    def log_agent_start(self, agent_name: str, **kwargs):
        """Log agent execution start"""
        self.logger.info(
            "agent.start",
            agent=agent_name,
            component=self.component,
            **kwargs
        )
        
    def log_agent_complete(self, agent_name: str, duration: float, **kwargs):
        """Log agent execution completion"""
        self.logger.info(
            "agent.complete",
            agent=agent_name,
            component=self.component,
            duration_seconds=duration,
            **kwargs
        )
        
    def log_agent_error(self, agent_name: str, error: str, **kwargs):
        """Log agent error"""
        self.logger.error(
            "agent.error",
            agent=agent_name,
            component=self.component,
            error=error,
            **kwargs
        )
        
    def log_tool_execution(self, tool_name: str, success: bool, duration: float, **kwargs):
        """Log tool execution"""
        self.logger.info(
            "tool.execution",
            tool=tool_name,
            component=self.component,
            success=success,
            duration_seconds=duration,
            **kwargs
        )
        
    def log_workflow_event(self, event_type: str, **kwargs):
        """Log workflow events"""
        self.logger.info(
            f"workflow.{event_type}",
            component=self.component,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )


class DistributedTracer:
    """
    Distributed tracing for agent workflows
    Tracks execution flow across agents
    """
    
    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.active_spans: Dict[str, str] = {}
        
    def start_trace(self, trace_id: str, operation: str, **metadata) -> str:
        """Start a new trace"""
        self.traces[trace_id] = {
            "trace_id": trace_id,
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "start_timestamp": time.time(),
            "spans": [],
            "metadata": metadata,
            "status": "in_progress"
        }
        return trace_id
        
    def start_span(
        self,
        trace_id: str,
        span_id: str,
        operation: str,
        **attributes
    ) -> str:
        """Start a span within a trace"""
        if trace_id not in self.traces:
            raise ValueError(f"Trace {trace_id} not found")
            
        span = {
            "span_id": span_id,
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "start_timestamp": time.time(),
            "attributes": attributes,
            "events": [],
            "status": "in_progress"
        }
        
        self.traces[trace_id]["spans"].append(span)
        self.active_spans[span_id] = trace_id
        
        return span_id
        
    def add_span_event(self, span_id: str, event: str, **attributes):
        """Add event to a span"""
        if span_id not in self.active_spans:
            return
            
        trace_id = self.active_spans[span_id]
        trace = self.traces[trace_id]
        
        for span in trace["spans"]:
            if span["span_id"] == span_id:
                span["events"].append({
                    "timestamp": datetime.now().isoformat(),
                    "event": event,
                    "attributes": attributes
                })
                break
                
    def end_span(self, span_id: str, **attributes):
        """End a span"""
        if span_id not in self.active_spans:
            return
            
        trace_id = self.active_spans[span_id]
        trace = self.traces[trace_id]
        
        for span in trace["spans"]:
            if span["span_id"] == span_id:
                span["end_time"] = datetime.now().isoformat()
                span["end_timestamp"] = time.time()
                span["duration_seconds"] = span["end_timestamp"] - span["start_timestamp"]
                span["status"] = "completed"
                span["attributes"].update(attributes)
                break
                
        del self.active_spans[span_id]
        
    def end_trace(self, trace_id: str, status: str = "completed", **metadata):
        """End a trace"""
        if trace_id not in self.traces:
            return
            
        trace = self.traces[trace_id]
        trace["end_time"] = datetime.now().isoformat()
        trace["end_timestamp"] = time.time()
        trace["duration_seconds"] = trace["end_timestamp"] - trace["start_timestamp"]
        trace["status"] = status
        trace["metadata"].update(metadata)
        
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID"""
        return self.traces.get(trace_id)
        
    def export_trace(self, trace_id: str) -> str:
        """Export trace as JSON"""
        trace = self.get_trace(trace_id)
        if trace:
            return json.dumps(trace, indent=2)
        return "{}"
        
    @contextmanager
    def trace_context(self, trace_id: str, operation: str, **metadata):
        """Context manager for tracing"""
        self.start_trace(trace_id, operation, **metadata)
        try:
            yield trace_id
        except Exception as e:
            self.end_trace(trace_id, status="error", error=str(e))
            raise
        else:
            self.end_trace(trace_id, status="completed")
            
    @contextmanager
    def span_context(self, trace_id: str, span_id: str, operation: str, **attributes):
        """Context manager for spans"""
        self.start_span(trace_id, span_id, operation, **attributes)
        try:
            yield span_id
        except Exception as e:
            self.add_span_event(span_id, "error", error=str(e))
            self.end_span(span_id, status="error")
            raise
        else:
            self.end_span(span_id, status="completed")


class MetricsCollector:
    """
    Prometheus metrics collection
    Tracks performance and business metrics
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        
        # Agent execution metrics
        self.agent_executions = Counter(
            'agent_executions_total',
            'Total agent executions',
            ['agent_name', 'status'],
            registry=self.registry
        )
        
        self.agent_duration = Histogram(
            'agent_duration_seconds',
            'Agent execution duration',
            ['agent_name'],
            registry=self.registry
        )
        
        # Disaster metrics
        self.disasters_detected = Counter(
            'disasters_detected_total',
            'Total disasters detected',
            ['city', 'disaster_type', 'severity'],
            registry=self.registry
        )
        
        self.alerts_sent = Counter(
            'alerts_sent_total',
            'Total alerts sent',
            ['city', 'severity', 'channel'],
            registry=self.registry
        )
        
        # Tool metrics
        self.tool_calls = Counter(
            'tool_calls_total',
            'Total tool calls',
            ['tool_name', 'status'],
            registry=self.registry
        )
        
        self.tool_duration = Histogram(
            'tool_duration_seconds',
            'Tool execution duration',
            ['tool_name'],
            registry=self.registry
        )
        
        # System metrics
        self.active_sessions = Gauge(
            'active_sessions',
            'Number of active sessions',
            registry=self.registry
        )
        
        self.memory_events = Gauge(
            'memory_events_total',
            'Total events in memory bank',
            registry=self.registry
        )
        
    def record_agent_execution(self, agent_name: str, duration: float, status: str):
        """Record agent execution"""
        self.agent_executions.labels(agent_name=agent_name, status=status).inc()
        self.agent_duration.labels(agent_name=agent_name).observe(duration)
        
    def record_disaster_detection(self, city: str, disaster_type: str, severity: str):
        """Record disaster detection"""
        self.disasters_detected.labels(
            city=city,
            disaster_type=disaster_type,
            severity=severity
        ).inc()
        
    def record_alert_sent(self, city: str, severity: str, channel: str = "email"):
        """Record alert sent"""
        self.alerts_sent.labels(city=city, severity=severity, channel=channel).inc()
        
    def record_tool_call(self, tool_name: str, duration: float, status: str):
        """Record tool call"""
        self.tool_calls.labels(tool_name=tool_name, status=status).inc()
        self.tool_duration.labels(tool_name=tool_name).observe(duration)
        
    def update_active_sessions(self, count: int):
        """Update active session count"""
        self.active_sessions.set(count)
        
    def update_memory_events(self, count: int):
        """Update memory event count"""
        self.memory_events.set(count)
        
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics"""
        return generate_latest(self.registry)


class ObservabilityManager:
    """
    Unified observability management
    Combines logging, tracing, and metrics
    """
    
    def __init__(self, component: str = "disaster_management"):
        self.logger = EventLogger(component)
        self.tracer = DistributedTracer()
        self.metrics = MetricsCollector()
        
    def observe_agent_execution(
        self,
        trace_id: str,
        agent_name: str,
        operation: str
    ):
        """Context manager for observing agent execution"""
        return AgentExecutionObserver(
            trace_id=trace_id,
            agent_name=agent_name,
            operation=operation,
            logger=self.logger,
            tracer=self.tracer,
            metrics=self.metrics
        )
        
    def observe_tool_call(
        self,
        trace_id: str,
        tool_name: str
    ):
        """Context manager for observing tool calls"""
        return ToolCallObserver(
            trace_id=trace_id,
            tool_name=tool_name,
            logger=self.logger,
            tracer=self.tracer,
            metrics=self.metrics
        )


class AgentExecutionObserver:
    """Context manager for observing agent execution"""
    
    def __init__(self, trace_id, agent_name, operation, logger, tracer, metrics):
        self.trace_id = trace_id
        self.agent_name = agent_name
        self.operation = operation
        self.logger = logger
        self.tracer = tracer
        self.metrics = metrics
        self.span_id = f"{agent_name}_{int(time.time() * 1000)}"
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log_agent_start(self.agent_name, operation=self.operation)
        self.tracer.start_span(self.trace_id, self.span_id, self.operation)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            status = "success"
            self.logger.log_agent_complete(self.agent_name, duration)
            self.tracer.end_span(self.span_id, status="completed")
        else:
            status = "error"
            self.logger.log_agent_error(self.agent_name, str(exc_val))
            self.tracer.add_span_event(self.span_id, "error", error=str(exc_val))
            self.tracer.end_span(self.span_id, status="error")
            
        self.metrics.record_agent_execution(self.agent_name, duration, status)
        return False


class ToolCallObserver:
    """Context manager for observing tool calls"""
    
    def __init__(self, trace_id, tool_name, logger, tracer, metrics):
        self.trace_id = trace_id
        self.tool_name = tool_name
        self.logger = logger
        self.tracer = tracer
        self.metrics = metrics
        self.span_id = f"tool_{tool_name}_{int(time.time() * 1000)}"
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.tracer.start_span(self.trace_id, self.span_id, f"tool_call_{self.tool_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "success" if exc_type is None else "error"
        
        self.logger.log_tool_execution(self.tool_name, status == "success", duration)
        self.tracer.end_span(self.span_id, status=status)
        self.metrics.record_tool_call(self.tool_name, duration, status)
        
        return False
