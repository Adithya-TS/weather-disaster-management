"""
Agent Evaluation Framework
Demonstrates automated testing and quality assessment
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import asyncio
import structlog

logger = structlog.get_logger()


class EvaluationCase(BaseModel):
    """Test case for agent evaluation"""
    case_id: str
    city: str
    simulated_weather: Dict[str, Any]
    expected_disaster_type: str
    expected_severity: str
    expected_response_type: str
    description: str
    
    class Config:
        arbitrary_types_allowed = True


class EvaluationResult(BaseModel):
    """Result of an evaluation"""
    case_id: str
    passed: bool
    disaster_type_match: bool
    severity_match: bool
    response_appropriate: bool
    execution_time: float
    error: Optional[str] = None
    details: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()
    
    class Config:
        arbitrary_types_allowed = True


class DisasterDetectionEvaluator:
    """
    Evaluates disaster detection accuracy
    """
    
    TEST_CASES = [
        EvaluationCase(
            case_id="hurricane_critical",
            city="Miami",
            simulated_weather={
                "weather": "severe storm with hurricane-force winds",
                "temperature": 28.0,
                "wind_speed": 55.0,  # Hurricane force
                "humidity": 95,
                "pressure": 950,
                "cloud_cover": 100
            },
            expected_disaster_type="Hurricane",
            expected_severity="Critical",
            expected_response_type="emergency",
            description="Critical hurricane scenario"
        ),
        EvaluationCase(
            case_id="flood_high",
            city="Houston",
            simulated_weather={
                "weather": "heavy rainfall and flooding",
                "temperature": 22.0,
                "wind_speed": 15.0,
                "humidity": 98,
                "pressure": 1000,
                "cloud_cover": 95
            },
            expected_disaster_type="Flood",
            expected_severity="High",
            expected_response_type="public_works",
            description="High severity flood scenario"
        ),
        EvaluationCase(
            case_id="heatwave_medium",
            city="Phoenix",
            simulated_weather={
                "weather": "clear sky with extreme heat",
                "temperature": 45.0,  # 113°F
                "wind_speed": 5.0,
                "humidity": 15,
                "pressure": 1010,
                "cloud_cover": 10
            },
            expected_disaster_type="Heatwave",
            expected_severity="Medium",
            expected_response_type="civil_defense",
            description="Medium severity heatwave"
        ),
        EvaluationCase(
            case_id="no_threat_low",
            city="Seattle",
            simulated_weather={
                "weather": "partly cloudy",
                "temperature": 18.0,
                "wind_speed": 8.0,
                "humidity": 60,
                "pressure": 1015,
                "cloud_cover": 40
            },
            expected_disaster_type="No Immediate Threat",
            expected_severity="Low",
            expected_response_type="none",
            description="Normal weather conditions"
        ),
    ]
    
    async def evaluate_agent(self, agent_executor) -> List[EvaluationResult]:
        """Evaluate agent against test cases"""
        logger.info("evaluation.disaster_detection.start", case_count=len(self.TEST_CASES))
        
        results = []
        for case in self.TEST_CASES:
            result = await self._evaluate_case(case, agent_executor)
            results.append(result)
            
        # Calculate overall metrics
        passed = sum(1 for r in results if r.passed)
        accuracy = passed / len(results) if results else 0
        
        logger.info(
            "evaluation.disaster_detection.complete",
            total_cases=len(results),
            passed=passed,
            accuracy=accuracy
        )
        
        return results
        
    async def _evaluate_case(
        self,
        case: EvaluationCase,
        agent_executor
    ) -> EvaluationResult:
        """Evaluate a single test case"""
        logger.info("evaluation.case.start", case_id=case.case_id)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create initial state with simulated data
            from ..agents.multi_agent_system import AgentState
            
            state = AgentState(
                city=case.city,
                weather_data=case.simulated_weather
            )
            
            # Execute agent workflow
            final_state = await agent_executor.execute(state)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Check results
            disaster_match = self._check_disaster_type(
                final_state.disaster_type,
                case.expected_disaster_type
            )
            
            severity_match = self._check_severity(
                final_state.severity,
                case.expected_severity
            )
            
            response_appropriate = self._check_response(
                final_state.response_plan,
                case.expected_response_type
            )
            
            passed = disaster_match and severity_match and response_appropriate
            
            result = EvaluationResult(
                case_id=case.case_id,
                passed=passed,
                disaster_type_match=disaster_match,
                severity_match=severity_match,
                response_appropriate=response_appropriate,
                execution_time=execution_time,
                details={
                    "actual_disaster_type": final_state.disaster_type,
                    "actual_severity": final_state.severity,
                    "expected_disaster_type": case.expected_disaster_type,
                    "expected_severity": case.expected_severity
                }
            )
            
            logger.info(
                "evaluation.case.complete",
                case_id=case.case_id,
                passed=passed,
                execution_time=execution_time
            )
            
            return result
            
        except Exception as e:
            logger.error("evaluation.case.error", case_id=case.case_id, error=str(e))
            
            return EvaluationResult(
                case_id=case.case_id,
                passed=False,
                disaster_type_match=False,
                severity_match=False,
                response_appropriate=False,
                execution_time=0,
                error=str(e)
            )
            
    def _check_disaster_type(self, actual: str, expected: str) -> bool:
        """Check if disaster type matches"""
        # Normalize and compare
        actual_lower = actual.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Allow partial matches
        return expected_lower in actual_lower or actual_lower in expected_lower
        
    def _check_severity(self, actual: str, expected: str) -> bool:
        """Check if severity matches"""
        actual_lower = actual.lower().strip()
        expected_lower = expected.lower().strip()
        
        return actual_lower == expected_lower
        
    def _check_response(self, response_plan: str, expected_type: str) -> bool:
        """Check if response is appropriate"""
        if expected_type == "none":
            return True  # Any response is fine for no threat
            
        response_lower = response_plan.lower()
        
        # Check for keywords indicating appropriate response
        if expected_type == "emergency":
            return any(word in response_lower for word in ["emergency", "evacuation", "critical"])
        elif expected_type == "public_works":
            return any(word in response_lower for word in ["infrastructure", "public works", "flood"])
        elif expected_type == "civil_defense":
            return any(word in response_lower for word in ["civil defense", "public safety", "shelter"])
            
        return True


class ResponseQualityEvaluator:
    """
    Evaluates quality of generated response plans
    """
    
    QUALITY_CRITERIA = [
        "specificity",  # Response should be specific to disaster type
        "actionability",  # Response should contain actionable steps
        "completeness",  # Response should cover preparation and response
        "clarity"  # Response should be clear and well-structured
    ]
    
    async def evaluate_response(
        self,
        response_plan: str,
        disaster_type: str,
        severity: str
    ) -> Dict[str, Any]:
        """Evaluate response plan quality"""
        logger.info(
            "evaluation.response_quality.start",
            disaster_type=disaster_type,
            severity=severity
        )
        
        scores = {}
        
        # Specificity: mentions disaster type
        scores["specificity"] = self._check_specificity(response_plan, disaster_type)
        
        # Actionability: contains numbered steps or action verbs
        scores["actionability"] = self._check_actionability(response_plan)
        
        # Completeness: covers multiple aspects
        scores["completeness"] = self._check_completeness(response_plan)
        
        # Clarity: well-structured and readable
        scores["clarity"] = self._check_clarity(response_plan)
        
        # Overall score
        overall_score = sum(scores.values()) / len(scores)
        
        result = {
            "scores": scores,
            "overall_score": overall_score,
            "passed": overall_score >= 0.7,  # 70% threshold
            "response_length": len(response_plan),
            "disaster_type": disaster_type,
            "severity": severity
        }
        
        logger.info(
            "evaluation.response_quality.complete",
            overall_score=overall_score,
            passed=result["passed"]
        )
        
        return result
        
    def _check_specificity(self, response: str, disaster_type: str) -> float:
        """Check if response is specific to disaster type"""
        keywords = disaster_type.lower().split()
        mentions = sum(1 for keyword in keywords if keyword in response.lower())
        return min(mentions / len(keywords), 1.0) if keywords else 0.5
        
    def _check_actionability(self, response: str) -> float:
        """Check if response contains actionable items"""
        action_indicators = [
            "1.", "2.", "3.",  # Numbered lists
            "evacuate", "prepare", "monitor", "contact", "ensure", "activate"
        ]
        
        score = sum(1 for indicator in action_indicators if indicator in response.lower())
        return min(score / 5, 1.0)  # Normalize to 0-1
        
    def _check_completeness(self, response: str) -> float:
        """Check if response covers multiple aspects"""
        aspects = ["prepare", "respond", "monitor", "coordinate", "communicate"]
        covered = sum(1 for aspect in aspects if aspect in response.lower())
        return covered / len(aspects)
        
    def _check_clarity(self, response: str) -> float:
        """Check if response is clear and well-structured"""
        # Simple heuristics
        has_structure = any(char in response for char in ["1.", "-", "*"])
        reasonable_length = 100 < len(response) < 1000
        has_periods = response.count(".") >= 2
        
        score = sum([has_structure, reasonable_length, has_periods]) / 3
        return score


class PerformanceBenchmark:
    """
    Benchmarks agent performance
    """
    
    async def run_benchmark(
        self,
        agent_executor,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Run performance benchmark"""
        logger.info("benchmark.start", iterations=iterations)
        
        execution_times = []
        
        for i in range(iterations):
            start = asyncio.get_event_loop().time()
            
            try:
                from ..agents.multi_agent_system import AgentState
                
                state = AgentState(
                    city="TestCity",
                    weather_data={
                        "weather": "test",
                        "temperature": 20.0,
                        "wind_speed": 10.0,
                        "humidity": 50,
                        "pressure": 1010,
                        "cloud_cover": 50
                    }
                )
                
                await agent_executor.execute(state)
                
                elapsed = asyncio.get_event_loop().time() - start
                execution_times.append(elapsed)
                
            except Exception as e:
                logger.error("benchmark.iteration.error", iteration=i, error=str(e))
                
        if not execution_times:
            return {"error": "No successful iterations"}
            
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        result = {
            "iterations": len(execution_times),
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "throughput": 1 / avg_time if avg_time > 0 else 0  # requests per second
        }
        
        logger.info("benchmark.complete", **result)
        return result


class EvaluationSuite:
    """
    Complete evaluation suite
    """
    
    def __init__(self):
        self.disaster_evaluator = DisasterDetectionEvaluator()
        self.quality_evaluator = ResponseQualityEvaluator()
        self.benchmark = PerformanceBenchmark()
        
    async def run_full_evaluation(self, agent_executor) -> Dict[str, Any]:
        """Run complete evaluation suite"""
        logger.info("evaluation_suite.start")
        
        # Disaster detection evaluation
        detection_results = await self.disaster_evaluator.evaluate_agent(agent_executor)
        
        # Performance benchmark
        benchmark_results = await self.benchmark.run_benchmark(agent_executor)
        
        # Summary
        detection_accuracy = sum(1 for r in detection_results if r.passed) / len(detection_results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "detection_accuracy": detection_accuracy,
            "test_cases_passed": sum(1 for r in detection_results if r.passed),
            "test_cases_total": len(detection_results),
            "average_execution_time": benchmark_results.get("average_time", 0),
            "throughput": benchmark_results.get("throughput", 0),
            "detailed_results": {
                "detection": [r.dict() for r in detection_results],
                "benchmark": benchmark_results
            }
        }
        
        logger.info(
            "evaluation_suite.complete",
            detection_accuracy=detection_accuracy,
            throughput=summary["throughput"]
        )
        
        return summary
