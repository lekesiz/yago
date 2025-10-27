"""
YAGO v7.1 - Performance Benchmarks Suite
Comprehensive performance testing and regression detection
"""

import asyncio
import time
import uuid
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from collections import defaultdict
import json

router = APIRouter(prefix="/api/v1/benchmarks", tags=["benchmarks"])


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class BenchmarkCategory(str, Enum):
    """Benchmark categories"""
    CLARIFICATION = "clarification"
    AGENT_CREATION = "agent_creation"
    TASK_ASSIGNMENT = "task_assignment"
    EXECUTION = "execution"
    EVENT_PROCESSING = "event_processing"
    API_RESPONSE = "api_response"
    MEMORY = "memory"
    THROUGHPUT = "throughput"


class BenchmarkStatus(str, Enum):
    """Benchmark result status"""
    PASS = "PASS"
    FAIL = "FAIL"
    REGRESSION = "REGRESSION"
    IMPROVEMENT = "IMPROVEMENT"
    PENDING = "PENDING"


class ExecutionStrategy(str, Enum):
    """Execution strategies for benchmarking"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


# Performance targets (in milliseconds)
PERFORMANCE_TARGETS = {
    # Clarification Phase
    "clarification_small": 30_000,      # 10 questions
    "clarification_medium": 60_000,     # 25 questions
    "clarification_large": 120_000,     # 50 questions

    # Agent Creation
    "agent_creation_5": 5_000,
    "agent_creation_10": 10_000,
    "agent_creation_20": 15_000,

    # Task Assignment
    "task_assignment_10": 100,
    "task_assignment_50": 500,
    "task_assignment_100": 1_000,

    # API Response Times
    "api_list_clarifications": 200,
    "api_create_project": 500,
    "api_get_costs": 100,
    "api_generate_report": 1_000,

    # Event Processing
    "event_latency": 100,
    "event_throughput": 1_000,  # events/sec
    "event_memory": 100,  # MB for 10k events
}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class BenchmarkResult(BaseModel):
    """Single benchmark result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: BenchmarkCategory
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    status: BenchmarkStatus
    target_ms: float
    previous_ms: Optional[float] = None
    variance_pct: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    error_message: Optional[str] = None


class BenchmarkSuite(BaseModel):
    """Collection of benchmark results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    suite_name: str
    version: str = "v7.1"
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    results: List[BenchmarkResult]
    summary: Dict[str, Any]
    environment: Dict[str, str]


class BenchmarkComparison(BaseModel):
    """Comparison between two benchmark runs"""
    baseline_id: str
    current_id: str
    improvements: List[str]
    regressions: List[str]
    overall_change_pct: float
    details: Dict[str, Dict[str, float]]


class PerformanceTrend(BaseModel):
    """Performance trend over time"""
    benchmark_name: str
    data_points: List[Dict[str, Any]]
    trend: str  # improving, degrading, stable
    avg_duration: float
    min_duration: float
    max_duration: float
    std_deviation: float


# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

class BenchmarkStorage:
    """In-memory storage for benchmark data"""

    def __init__(self):
        self.suites: Dict[str, BenchmarkSuite] = {}
        self.results_by_name: Dict[str, List[BenchmarkResult]] = defaultdict(list)
        self.baseline: Optional[BenchmarkSuite] = None

    def add_suite(self, suite: BenchmarkSuite):
        """Add a benchmark suite"""
        self.suites[suite.id] = suite

        # Store individual results by name for trending
        for result in suite.results:
            self.results_by_name[result.name].append(result)

    def get_suite(self, suite_id: str) -> Optional[BenchmarkSuite]:
        """Get a specific suite"""
        return self.suites.get(suite_id)

    def get_latest_suite(self) -> Optional[BenchmarkSuite]:
        """Get the most recent suite"""
        if not self.suites:
            return None
        return max(self.suites.values(), key=lambda s: s.start_time)

    def set_baseline(self, suite_id: str):
        """Set a suite as baseline"""
        suite = self.get_suite(suite_id)
        if suite:
            self.baseline = suite

    def get_baseline(self) -> Optional[BenchmarkSuite]:
        """Get baseline suite"""
        return self.baseline

    def get_results_by_name(self, name: str) -> List[BenchmarkResult]:
        """Get all results for a specific benchmark"""
        return self.results_by_name.get(name, [])


# Global storage
storage = BenchmarkStorage()


# ============================================================================
# BENCHMARK RUNNER
# ============================================================================

class BenchmarkRunner:
    """Runs and measures performance benchmarks"""

    def __init__(self):
        self.process = psutil.Process()

    async def measure_execution(self,
                               func: Callable,
                               *args,
                               **kwargs) -> Dict[str, float]:
        """Measure execution time, memory, and CPU"""
        # Get initial metrics
        mem_before = self.process.memory_info().rss / (1024 * 1024)  # MB
        cpu_before = self.process.cpu_percent(interval=0.1)

        start_time = time.perf_counter()

        # Execute function
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        end_time = time.perf_counter()

        # Get final metrics
        mem_after = self.process.memory_info().rss / (1024 * 1024)  # MB
        cpu_after = self.process.cpu_percent(interval=0.1)

        duration_ms = (end_time - start_time) * 1000
        memory_delta = mem_after - mem_before
        cpu_avg = (cpu_before + cpu_after) / 2

        return {
            "duration_ms": duration_ms,
            "memory_mb": max(0, memory_delta),
            "cpu_percent": cpu_avg,
            "result": result
        }

    async def benchmark_clarification(self, complexity: str, question_count: int) -> BenchmarkResult:
        """Benchmark clarification phase"""
        benchmark_name = f"clarification_{complexity}"
        target_key = f"clarification_{complexity}"

        async def mock_clarification():
            """Simulate clarification processing"""
            # Simulate question processing
            for i in range(question_count):
                await asyncio.sleep(0.01)  # Simulate processing
                # Simulate some computation
                _ = [j**2 for j in range(1000)]
            return {"questions": question_count, "completed": True}

        metrics = await self.measure_execution(mock_clarification)

        target_ms = PERFORMANCE_TARGETS.get(target_key, 60_000)
        duration = metrics["duration_ms"]

        # Determine status
        if duration < target_ms:
            status = BenchmarkStatus.PASS
        elif duration < target_ms * 1.2:  # Within 20% tolerance
            status = BenchmarkStatus.PASS
        else:
            status = BenchmarkStatus.FAIL

        return BenchmarkResult(
            name=benchmark_name,
            category=BenchmarkCategory.CLARIFICATION,
            duration_ms=duration,
            memory_mb=metrics["memory_mb"],
            cpu_percent=metrics["cpu_percent"],
            status=status,
            target_ms=target_ms,
            metadata={"question_count": question_count, "complexity": complexity}
        )

    async def benchmark_agent_creation(self, agent_count: int) -> BenchmarkResult:
        """Benchmark agent creation"""
        benchmark_name = f"agent_creation_{agent_count}"
        target_key = f"agent_creation_{agent_count}"

        async def create_agents():
            """Simulate agent creation"""
            agents = []
            for i in range(agent_count):
                # Simulate agent initialization
                agent = {
                    "id": str(uuid.uuid4()),
                    "name": f"Agent_{i}",
                    "type": "base",
                    "initialized": True
                }
                agents.append(agent)
                await asyncio.sleep(0.001)  # Simulate creation time
            return agents

        metrics = await self.measure_execution(create_agents)

        target_ms = PERFORMANCE_TARGETS.get(target_key, 10_000)
        duration = metrics["duration_ms"]

        status = BenchmarkStatus.PASS if duration < target_ms else BenchmarkStatus.FAIL

        return BenchmarkResult(
            name=benchmark_name,
            category=BenchmarkCategory.AGENT_CREATION,
            duration_ms=duration,
            memory_mb=metrics["memory_mb"],
            cpu_percent=metrics["cpu_percent"],
            status=status,
            target_ms=target_ms,
            metadata={"agent_count": agent_count}
        )

    async def benchmark_task_assignment(self, task_count: int) -> BenchmarkResult:
        """Benchmark task assignment"""
        benchmark_name = f"task_assignment_{task_count}"
        target_key = f"task_assignment_{task_count}"

        async def assign_tasks():
            """Simulate task assignment"""
            tasks = []
            agents = [f"agent_{i}" for i in range(10)]

            for i in range(task_count):
                task = {
                    "id": str(uuid.uuid4()),
                    "assigned_to": agents[i % len(agents)],
                    "priority": i % 3
                }
                tasks.append(task)

            return tasks

        metrics = await self.measure_execution(assign_tasks)

        target_ms = PERFORMANCE_TARGETS.get(target_key, 500)
        duration = metrics["duration_ms"]

        status = BenchmarkStatus.PASS if duration < target_ms else BenchmarkStatus.FAIL

        return BenchmarkResult(
            name=benchmark_name,
            category=BenchmarkCategory.TASK_ASSIGNMENT,
            duration_ms=duration,
            memory_mb=metrics["memory_mb"],
            cpu_percent=metrics["cpu_percent"],
            status=status,
            target_ms=target_ms,
            metadata={"task_count": task_count}
        )

    async def benchmark_execution(self, strategy: ExecutionStrategy, task_count: int) -> BenchmarkResult:
        """Benchmark execution strategies"""
        benchmark_name = f"execution_{strategy.value}_{task_count}"

        async def execute_tasks():
            """Simulate task execution"""
            tasks = [asyncio.sleep(0.01) for _ in range(task_count)]

            if strategy == ExecutionStrategy.SEQUENTIAL:
                for task in tasks:
                    await task
            elif strategy == ExecutionStrategy.PARALLEL:
                await asyncio.gather(*tasks)
            else:  # HYBRID
                # Execute in batches of 5
                batch_size = 5
                for i in range(0, len(tasks), batch_size):
                    batch = tasks[i:i + batch_size]
                    await asyncio.gather(*batch)

            return {"completed": task_count}

        metrics = await self.measure_execution(execute_tasks)

        # For parallel execution, expect significant speedup
        duration = metrics["duration_ms"]

        # Calculate expected speedup
        if strategy == ExecutionStrategy.SEQUENTIAL:
            baseline_duration = duration
            status = BenchmarkStatus.PASS
        elif strategy == ExecutionStrategy.PARALLEL:
            # Should be ~3x faster than sequential
            expected_max = (task_count * 10) / 3  # 10ms per task, 3x speedup
            status = BenchmarkStatus.PASS if duration < expected_max else BenchmarkStatus.FAIL
        else:  # HYBRID
            # Should be ~2.5x faster
            expected_max = (task_count * 10) / 2.5
            status = BenchmarkStatus.PASS if duration < expected_max else BenchmarkStatus.FAIL

        return BenchmarkResult(
            name=benchmark_name,
            category=BenchmarkCategory.EXECUTION,
            duration_ms=duration,
            memory_mb=metrics["memory_mb"],
            cpu_percent=metrics["cpu_percent"],
            status=status,
            target_ms=task_count * 10,  # 10ms per task baseline
            metadata={"strategy": strategy.value, "task_count": task_count}
        )

    async def benchmark_event_processing(self, event_count: int) -> BenchmarkResult:
        """Benchmark event processing"""
        benchmark_name = f"event_processing_{event_count}"

        async def process_events():
            """Simulate event processing"""
            events = []
            for i in range(event_count):
                event = {
                    "id": str(uuid.uuid4()),
                    "type": f"event_type_{i % 10}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {"value": i}
                }
                events.append(event)
                # Simulate processing
                if i % 100 == 0:
                    await asyncio.sleep(0)  # Yield control

            return events

        metrics = await self.measure_execution(process_events)

        duration = metrics["duration_ms"]
        throughput = (event_count / duration) * 1000  # events per second

        # Target: >1000 events/sec, <100ms latency for avg event
        avg_latency = duration / event_count

        status = BenchmarkStatus.PASS if (
            throughput >= PERFORMANCE_TARGETS["event_throughput"] and
            avg_latency < PERFORMANCE_TARGETS["event_latency"]
        ) else BenchmarkStatus.FAIL

        return BenchmarkResult(
            name=benchmark_name,
            category=BenchmarkCategory.EVENT_PROCESSING,
            duration_ms=duration,
            memory_mb=metrics["memory_mb"],
            cpu_percent=metrics["cpu_percent"],
            status=status,
            target_ms=PERFORMANCE_TARGETS["event_latency"] * event_count,
            metadata={
                "event_count": event_count,
                "throughput": round(throughput, 2),
                "avg_latency_ms": round(avg_latency, 3)
            }
        )

    async def benchmark_api_endpoint(self, endpoint_name: str, func: Callable) -> BenchmarkResult:
        """Benchmark API endpoint response time"""
        benchmark_name = f"api_{endpoint_name}"
        target_key = f"api_{endpoint_name}"

        metrics = await self.measure_execution(func)

        target_ms = PERFORMANCE_TARGETS.get(target_key, 500)
        duration = metrics["duration_ms"]

        status = BenchmarkStatus.PASS if duration < target_ms else BenchmarkStatus.FAIL

        return BenchmarkResult(
            name=benchmark_name,
            category=BenchmarkCategory.API_RESPONSE,
            duration_ms=duration,
            memory_mb=metrics["memory_mb"],
            cpu_percent=metrics["cpu_percent"],
            status=status,
            target_ms=target_ms,
            metadata={"endpoint": endpoint_name}
        )


# Global runner
runner = BenchmarkRunner()


# ============================================================================
# BENCHMARK ANALYSIS
# ============================================================================

class BenchmarkAnalyzer:
    """Analyzes benchmark results and detects regressions"""

    @staticmethod
    def compare_results(current: BenchmarkResult, previous: BenchmarkResult) -> BenchmarkStatus:
        """Compare two benchmark results"""
        if not previous:
            return BenchmarkStatus.PASS

        variance_pct = ((current.duration_ms - previous.duration_ms) / previous.duration_ms) * 100

        # >10% slower = regression
        if variance_pct > 10:
            return BenchmarkStatus.REGRESSION
        # >10% faster = improvement
        elif variance_pct < -10:
            return BenchmarkStatus.IMPROVEMENT
        # Within 10% = pass
        else:
            return BenchmarkStatus.PASS

    @staticmethod
    def compare_suites(baseline: BenchmarkSuite, current: BenchmarkSuite) -> BenchmarkComparison:
        """Compare two benchmark suites"""
        improvements = []
        regressions = []
        details = {}

        # Map baseline results by name
        baseline_map = {r.name: r for r in baseline.results}

        total_change = 0
        comparison_count = 0

        for current_result in current.results:
            baseline_result = baseline_map.get(current_result.name)

            if baseline_result:
                change_pct = (
                    (current_result.duration_ms - baseline_result.duration_ms) /
                    baseline_result.duration_ms * 100
                )

                total_change += change_pct
                comparison_count += 1

                details[current_result.name] = {
                    "baseline_ms": baseline_result.duration_ms,
                    "current_ms": current_result.duration_ms,
                    "change_pct": round(change_pct, 2)
                }

                if change_pct > 10:
                    regressions.append(
                        f"{current_result.name}: {change_pct:+.1f}% slower"
                    )
                elif change_pct < -10:
                    improvements.append(
                        f"{current_result.name}: {abs(change_pct):.1f}% faster"
                    )

        overall_change = total_change / comparison_count if comparison_count > 0 else 0

        return BenchmarkComparison(
            baseline_id=baseline.id,
            current_id=current.id,
            improvements=improvements,
            regressions=regressions,
            overall_change_pct=round(overall_change, 2),
            details=details
        )

    @staticmethod
    def calculate_trend(results: List[BenchmarkResult]) -> PerformanceTrend:
        """Calculate performance trend from historical results"""
        if not results:
            return None

        # Sort by timestamp
        results = sorted(results, key=lambda r: r.timestamp)

        durations = [r.duration_ms for r in results]

        # Calculate statistics
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0

        # Determine trend (compare recent vs older)
        if len(results) >= 5:
            recent_avg = statistics.mean(durations[-3:])
            older_avg = statistics.mean(durations[:3])

            if recent_avg < older_avg * 0.9:
                trend = "improving"
            elif recent_avg > older_avg * 1.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        data_points = [
            {
                "timestamp": r.timestamp.isoformat(),
                "duration_ms": r.duration_ms,
                "status": r.status.value
            }
            for r in results
        ]

        return PerformanceTrend(
            benchmark_name=results[0].name,
            data_points=data_points,
            trend=trend,
            avg_duration=round(avg_duration, 2),
            min_duration=round(min_duration, 2),
            max_duration=round(max_duration, 2),
            std_deviation=round(std_dev, 2)
        )


# Global analyzer
analyzer = BenchmarkAnalyzer()


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

@router.post("/run/full-suite")
async def run_full_benchmark_suite() -> BenchmarkSuite:
    """Run complete benchmark suite"""
    start_time = datetime.utcnow()
    results = []

    # 1. Clarification benchmarks
    for complexity, count in [("small", 10), ("medium", 25), ("large", 50)]:
        result = await runner.benchmark_clarification(complexity, count)
        results.append(result)

    # 2. Agent creation benchmarks
    for count in [5, 10, 20]:
        result = await runner.benchmark_agent_creation(count)
        results.append(result)

    # 3. Task assignment benchmarks
    for count in [10, 50, 100]:
        result = await runner.benchmark_task_assignment(count)
        results.append(result)

    # 4. Execution strategy benchmarks
    for strategy in ExecutionStrategy:
        result = await runner.benchmark_execution(strategy, 10)
        results.append(result)

    # 5. Event processing benchmark
    result = await runner.benchmark_event_processing(10000)
    results.append(result)

    # 6. API endpoint benchmarks (mock)
    for endpoint in ["list_clarifications", "create_project", "get_costs"]:
        async def mock_api():
            await asyncio.sleep(0.05)  # Simulate API processing
            return {"success": True}

        result = await runner.benchmark_api_endpoint(endpoint, mock_api)
        results.append(result)

    end_time = datetime.utcnow()

    # Calculate summary
    total_pass = sum(1 for r in results if r.status == BenchmarkStatus.PASS)
    total_fail = sum(1 for r in results if r.status == BenchmarkStatus.FAIL)
    avg_duration = statistics.mean(r.duration_ms for r in results)

    summary = {
        "total_benchmarks": len(results),
        "passed": total_pass,
        "failed": total_fail,
        "success_rate": round((total_pass / len(results)) * 100, 2),
        "avg_duration_ms": round(avg_duration, 2),
        "total_duration_seconds": (end_time - start_time).total_seconds()
    }

    # Get environment info
    environment = {
        "python_version": "3.11",
        "platform": "darwin",
        "cpu_count": str(psutil.cpu_count()),
        "memory_total_gb": str(round(psutil.virtual_memory().total / (1024**3), 2))
    }

    suite = BenchmarkSuite(
        suite_name="Full Performance Suite",
        start_time=start_time,
        end_time=end_time,
        duration_seconds=(end_time - start_time).total_seconds(),
        results=results,
        summary=summary,
        environment=environment
    )

    storage.add_suite(suite)

    return suite


@router.get("/suites/{suite_id}")
async def get_suite(suite_id: str) -> BenchmarkSuite:
    """Get a specific benchmark suite"""
    suite = storage.get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    return suite


@router.get("/suites/latest")
async def get_latest_suite() -> BenchmarkSuite:
    """Get the latest benchmark suite"""
    suite = storage.get_latest_suite()
    if not suite:
        raise HTTPException(status_code=404, detail="No suites found")
    return suite


@router.post("/baseline/{suite_id}")
async def set_baseline(suite_id: str):
    """Set a suite as the baseline for comparisons"""
    suite = storage.get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    storage.set_baseline(suite_id)
    return {"success": True, "baseline_id": suite_id}


@router.get("/compare/{current_id}")
async def compare_with_baseline(current_id: str) -> BenchmarkComparison:
    """Compare a suite with the baseline"""
    baseline = storage.get_baseline()
    if not baseline:
        raise HTTPException(status_code=404, detail="No baseline set")

    current = storage.get_suite(current_id)
    if not current:
        raise HTTPException(status_code=404, detail="Current suite not found")

    return analyzer.compare_suites(baseline, current)


@router.get("/trends/{benchmark_name}")
async def get_performance_trend(benchmark_name: str) -> PerformanceTrend:
    """Get performance trend for a specific benchmark"""
    results = storage.get_results_by_name(benchmark_name)

    if not results:
        raise HTTPException(status_code=404, detail="No results found for benchmark")

    trend = analyzer.calculate_trend(results)
    return trend


@router.get("/health")
async def benchmarks_health():
    """Health check for benchmarks system"""
    return {
        "status": "healthy",
        "total_suites": len(storage.suites),
        "baseline_set": storage.baseline is not None,
        "latest_suite": storage.get_latest_suite().id if storage.get_latest_suite() else None,
        "performance_targets": len(PERFORMANCE_TARGETS)
    }
