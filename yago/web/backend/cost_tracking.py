"""
YAGO v7.1 - Cost Tracking Dashboard
Real-time cost monitoring, optimization suggestions, and budget alerts
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from collections import defaultdict
import statistics

router = APIRouter(prefix="/api/v1/costs", tags=["costs"])


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ModelProvider(str, Enum):
    """AI Model providers"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"


class ModelName(str, Enum):
    """Specific model names"""
    CLAUDE_3_5_SONNET = "claude-3.5-sonnet"
    CLAUDE_3_OPUS = "claude-3-opus"
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GEMINI_2_0_FLASH = "gemini-2.0-flash-exp"
    GEMINI_1_5_PRO = "gemini-1.5-pro"


class ProjectPhase(str, Enum):
    """Project phases for cost breakdown"""
    CLARIFICATION = "clarification"
    PLANNING = "planning"
    CODING = "coding"
    TESTING = "testing"
    REVIEW = "review"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"


class AgentType(str, Enum):
    """Agent types (reusing from collaboration)"""
    PLANNER = "Planner"
    CODER = "Coder"
    TESTER = "Tester"
    REVIEWER = "Reviewer"
    DOCUMENTER = "Documenter"
    SECURITY = "SecurityAgent"
    DEVOPS = "DevOpsAgent"
    DATABASE = "DatabaseAgent"
    FRONTEND = "FrontendAgent"
    BACKEND = "BackendAgent"


# Model pricing (per 1M tokens)
MODEL_PRICING = {
    # Claude pricing (input / output per 1M tokens)
    ModelName.CLAUDE_3_5_SONNET: {"input": 3.00, "output": 15.00},
    ModelName.CLAUDE_3_OPUS: {"input": 15.00, "output": 75.00},

    # OpenAI pricing
    ModelName.GPT_4O: {"input": 2.50, "output": 10.00},
    ModelName.GPT_4_TURBO: {"input": 10.00, "output": 30.00},

    # Gemini pricing
    ModelName.GEMINI_2_0_FLASH: {"input": 0.075, "output": 0.30},
    ModelName.GEMINI_1_5_PRO: {"input": 1.25, "output": 5.00},
}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class APICall(BaseModel):
    """Single API call record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_id: str
    agent_type: AgentType
    model: ModelName
    provider: ModelProvider
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost: float
    duration_ms: int
    phase: ProjectPhase
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "success"  # success, error, timeout
    error_message: Optional[str] = None


class CostSummary(BaseModel):
    """Cost summary for a project"""
    project_id: str
    total_tokens: int
    total_api_calls: int
    total_cost: float
    start_date: datetime
    end_date: datetime

    # Breakdown by model
    cost_by_model: Dict[str, float]
    tokens_by_model: Dict[str, int]
    calls_by_model: Dict[str, int]

    # Breakdown by agent
    cost_by_agent: Dict[str, float]
    tokens_by_agent: Dict[str, int]
    calls_by_agent: Dict[str, int]

    # Breakdown by phase
    cost_by_phase: Dict[str, float]
    tokens_by_phase: Dict[str, int]

    # Performance metrics
    avg_cost_per_call: float
    avg_tokens_per_call: int
    avg_duration_ms: int

    # Efficiency
    cost_per_1k_tokens: float
    calls_per_hour: float


class AgentCosts(BaseModel):
    """Cost breakdown for a specific agent"""
    agent_id: str
    agent_type: AgentType
    project_id: str
    total_cost: float
    total_tokens: int
    total_calls: int
    avg_cost_per_call: float
    avg_tokens_per_call: int
    models_used: List[str]
    phases_active: List[str]
    first_call: datetime
    last_call: datetime
    efficiency_score: float  # 0-100


class Budget(BaseModel):
    """Budget configuration for a project"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    budget_limit: float
    alert_threshold: float = 0.75  # Alert at 75%
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class BudgetStatus(BaseModel):
    """Current budget status"""
    project_id: str
    budget: Budget
    current_spend: float
    remaining: float
    percentage_used: float
    is_over_budget: bool
    is_at_threshold: bool
    projected_final_cost: Optional[float] = None
    days_remaining: Optional[int] = None


class OptimizationSuggestion(BaseModel):
    """Cost optimization suggestion"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    description: str
    category: str  # model_selection, caching, parallelization, context_reduction
    potential_savings_pct: float
    potential_savings_amount: float
    priority: str  # low, medium, high
    implementation_difficulty: str  # easy, medium, hard
    details: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CostComparison(BaseModel):
    """Cost comparison metrics"""
    project_id: str
    estimated_cost: float
    actual_cost: float
    variance: float
    variance_pct: float
    team_average_cost: Optional[float] = None
    cost_per_feature: Optional[float] = None
    efficiency_vs_average: Optional[float] = None


class CostHistoryPoint(BaseModel):
    """Single point in cost history"""
    timestamp: datetime
    cumulative_cost: float
    tokens_used: int
    api_calls: int
    phase: Optional[ProjectPhase] = None


# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

class CostStorage:
    """In-memory storage for cost tracking data"""

    def __init__(self):
        self.api_calls: Dict[str, List[APICall]] = defaultdict(list)
        self.budgets: Dict[str, Budget] = {}
        self.project_estimates: Dict[str, float] = {}

    def add_api_call(self, call: APICall):
        """Add an API call record"""
        self.api_calls[call.project_id].append(call)

    def get_api_calls(self, project_id: str,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[APICall]:
        """Get API calls for a project, optionally filtered by date"""
        calls = self.api_calls.get(project_id, [])

        if start_date:
            calls = [c for c in calls if c.timestamp >= start_date]
        if end_date:
            calls = [c for c in calls if c.timestamp <= end_date]

        return calls

    def get_budget(self, project_id: str) -> Optional[Budget]:
        """Get budget for a project"""
        return self.budgets.get(project_id)

    def set_budget(self, budget: Budget):
        """Set or update budget"""
        self.budgets[budget.project_id] = budget

    def set_estimate(self, project_id: str, estimate: float):
        """Set cost estimate for a project"""
        self.project_estimates[project_id] = estimate

    def get_estimate(self, project_id: str) -> Optional[float]:
        """Get cost estimate"""
        return self.project_estimates.get(project_id)


# Global storage
storage = CostStorage()


# ============================================================================
# COST CALCULATOR
# ============================================================================

class CostCalculator:
    """Calculate costs based on token usage and model"""

    @staticmethod
    def calculate_cost(model: ModelName, tokens_input: int, tokens_output: int) -> float:
        """Calculate cost for a specific API call"""
        if model not in MODEL_PRICING:
            return 0.0

        pricing = MODEL_PRICING[model]

        # Cost = (input_tokens * input_price + output_tokens * output_price) / 1M
        cost = (tokens_input * pricing["input"] + tokens_output * pricing["output"]) / 1_000_000

        return round(cost, 6)

    @staticmethod
    def calculate_summary(calls: List[APICall]) -> Dict[str, Any]:
        """Calculate comprehensive cost summary from API calls"""
        if not calls:
            return {
                "total_cost": 0.0,
                "total_tokens": 0,
                "total_api_calls": 0,
                "avg_cost_per_call": 0.0,
                "avg_tokens_per_call": 0,
                "avg_duration_ms": 0,
            }

        total_cost = sum(c.cost for c in calls)
        total_tokens = sum(c.tokens_total for c in calls)
        total_calls = len(calls)

        # By model
        cost_by_model = defaultdict(float)
        tokens_by_model = defaultdict(int)
        calls_by_model = defaultdict(int)

        for call in calls:
            model_key = call.model.value
            cost_by_model[model_key] += call.cost
            tokens_by_model[model_key] += call.tokens_total
            calls_by_model[model_key] += 1

        # By agent
        cost_by_agent = defaultdict(float)
        tokens_by_agent = defaultdict(int)
        calls_by_agent = defaultdict(int)

        for call in calls:
            agent_key = call.agent_type.value
            cost_by_agent[agent_key] += call.cost
            tokens_by_agent[agent_key] += call.tokens_total
            calls_by_agent[agent_key] += 1

        # By phase
        cost_by_phase = defaultdict(float)
        tokens_by_phase = defaultdict(int)

        for call in calls:
            phase_key = call.phase.value
            cost_by_phase[phase_key] += call.cost
            tokens_by_phase[phase_key] += call.tokens_total

        # Averages
        avg_cost = total_cost / total_calls
        avg_tokens = total_tokens // total_calls
        avg_duration = statistics.mean(c.duration_ms for c in calls)

        # Time range
        start_date = min(c.timestamp for c in calls)
        end_date = max(c.timestamp for c in calls)
        duration_hours = (end_date - start_date).total_seconds() / 3600
        calls_per_hour = total_calls / max(duration_hours, 0.01)

        return {
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_api_calls": total_calls,
            "cost_by_model": dict(cost_by_model),
            "tokens_by_model": dict(tokens_by_model),
            "calls_by_model": dict(calls_by_model),
            "cost_by_agent": dict(cost_by_agent),
            "tokens_by_agent": dict(tokens_by_agent),
            "calls_by_agent": dict(calls_by_agent),
            "cost_by_phase": dict(cost_by_phase),
            "tokens_by_phase": dict(tokens_by_phase),
            "avg_cost_per_call": round(avg_cost, 4),
            "avg_tokens_per_call": avg_tokens,
            "avg_duration_ms": round(avg_duration),
            "cost_per_1k_tokens": round((total_cost / total_tokens * 1000), 4) if total_tokens > 0 else 0,
            "calls_per_hour": round(calls_per_hour, 2),
            "start_date": start_date,
            "end_date": end_date,
        }


# ============================================================================
# OPTIMIZATION SUGGESTION ENGINE
# ============================================================================

class OptimizationEngine:
    """Generate cost optimization suggestions"""

    @staticmethod
    def analyze_and_suggest(project_id: str, calls: List[APICall],
                           budget: Optional[Budget] = None) -> List[OptimizationSuggestion]:
        """Analyze usage patterns and generate suggestions"""
        suggestions = []

        if not calls:
            return suggestions

        # Calculate current stats
        summary = CostCalculator.calculate_summary(calls)
        total_cost = summary["total_cost"]
        cost_by_model = summary["cost_by_model"]
        calls_by_model = summary["calls_by_model"]

        # 1. Model Selection Optimization
        expensive_models_usage = sum(
            calls_by_model.get(model.value, 0)
            for model in [ModelName.CLAUDE_3_OPUS, ModelName.GPT_4_TURBO]
        )

        if expensive_models_usage > 0:
            # Calculate potential savings
            avg_expensive_cost = sum(
                cost_by_model.get(model.value, 0)
                for model in [ModelName.CLAUDE_3_OPUS, ModelName.GPT_4_TURBO]
            ) / expensive_models_usage

            potential_savings = avg_expensive_cost * expensive_models_usage * 0.6  # 60% cheaper

            suggestions.append(OptimizationSuggestion(
                project_id=project_id,
                title="Switch to more cost-effective models",
                description=f"You're using expensive models ({expensive_models_usage} calls). Consider using Claude 3.5 Sonnet or GPT-4o for similar quality at lower cost.",
                category="model_selection",
                potential_savings_pct=40.0,
                potential_savings_amount=round(potential_savings, 4),
                priority="high",
                implementation_difficulty="easy",
                details={
                    "expensive_calls": expensive_models_usage,
                    "recommended_models": ["claude-3.5-sonnet", "gpt-4o"],
                    "avg_savings_per_call": round(avg_expensive_cost * 0.4, 4)
                }
            ))

        # 2. Context Window Optimization
        avg_tokens = summary["avg_tokens_per_call"]
        if avg_tokens > 50000:
            potential_savings = total_cost * 0.15

            suggestions.append(OptimizationSuggestion(
                project_id=project_id,
                title="Reduce context window size",
                description=f"Average of {avg_tokens:,} tokens per call is high. Reducing context can save costs without sacrificing quality.",
                category="context_reduction",
                potential_savings_pct=15.0,
                potential_savings_amount=round(potential_savings, 4),
                priority="medium",
                implementation_difficulty="medium",
                details={
                    "current_avg_tokens": avg_tokens,
                    "recommended_max": 40000,
                    "methods": ["Summarize previous context", "Use RAG for relevant retrieval", "Chunk large inputs"]
                }
            ))

        # 3. Caching Opportunities
        # Count duplicate or similar calls
        phase_call_counts = summary["calls_by_agent"]
        high_volume_agents = {k: v for k, v in phase_call_counts.items() if v > 10}

        if high_volume_agents:
            potential_savings = total_cost * 0.25

            suggestions.append(OptimizationSuggestion(
                project_id=project_id,
                title="Implement response caching",
                description="High call volume detected. Caching common queries can reduce redundant API calls significantly.",
                category="caching",
                potential_savings_pct=25.0,
                potential_savings_amount=round(potential_savings, 4),
                priority="high",
                implementation_difficulty="medium",
                details={
                    "high_volume_agents": high_volume_agents,
                    "cache_strategies": ["Redis cache for common queries", "Semantic cache for similar questions", "Agent output memoization"]
                }
            ))

        # 4. Parallel Execution
        calls_per_hour = summary["calls_per_hour"]
        if calls_per_hour < 10 and len(calls) > 20:
            suggestions.append(OptimizationSuggestion(
                project_id=project_id,
                title="Increase parallelization",
                description=f"Only {calls_per_hour:.1f} calls/hour. Running agents in parallel can complete projects 20-40% faster.",
                category="parallelization",
                potential_savings_pct=0.0,  # Time savings, not cost
                potential_savings_amount=0.0,
                priority="low",
                implementation_difficulty="hard",
                details={
                    "current_calls_per_hour": round(calls_per_hour, 2),
                    "target_calls_per_hour": 30,
                    "time_savings_pct": 30,
                    "methods": ["Async agent execution", "Parallel task processing", "Batch API calls"]
                }
            ))

        # 5. Budget Warning
        if budget and budget.is_active:
            current_spend = total_cost
            budget_usage_pct = (current_spend / budget.budget_limit) * 100

            if budget_usage_pct > 80:
                suggestions.append(OptimizationSuggestion(
                    project_id=project_id,
                    title=f"⚠️ Budget Alert: {budget_usage_pct:.1f}% used",
                    description=f"You've used ${current_spend:.2f} of ${budget.budget_limit:.2f} budget. Consider cost-saving measures immediately.",
                    category="budget_alert",
                    potential_savings_pct=0.0,
                    potential_savings_amount=budget.budget_limit - current_spend,
                    priority="critical",
                    implementation_difficulty="easy",
                    details={
                        "budget_limit": budget.budget_limit,
                        "current_spend": round(current_spend, 4),
                        "remaining": round(budget.budget_limit - current_spend, 4),
                        "usage_pct": round(budget_usage_pct, 2)
                    }
                ))

        return suggestions


# Global engines
calculator = CostCalculator()
optimizer = OptimizationEngine()


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

@router.post("/track")
async def track_api_call(call: APICall):
    """Track a single API call"""
    # Calculate cost if not provided
    if call.cost == 0:
        call.cost = calculator.calculate_cost(
            call.model,
            call.tokens_input,
            call.tokens_output
        )

    storage.add_api_call(call)

    return {
        "success": True,
        "call_id": call.id,
        "cost": call.cost,
        "timestamp": call.timestamp.isoformat()
    }


@router.get("/summary/{project_id}", response_model=CostSummary)
async def get_cost_summary(
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get comprehensive cost summary for a project"""
    # Parse dates if provided
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    calls = storage.get_api_calls(project_id, start_dt, end_dt)

    if not calls:
        raise HTTPException(status_code=404, detail="No cost data found for project")

    summary_data = calculator.calculate_summary(calls)

    return CostSummary(
        project_id=project_id,
        **summary_data
    )


@router.get("/agent/{project_id}/{agent_type}", response_model=AgentCosts)
async def get_agent_costs(project_id: str, agent_type: AgentType):
    """Get cost breakdown for a specific agent"""
    all_calls = storage.get_api_calls(project_id)
    agent_calls = [c for c in all_calls if c.agent_type == agent_type]

    if not agent_calls:
        raise HTTPException(status_code=404, detail=f"No data found for agent {agent_type}")

    total_cost = sum(c.cost for c in agent_calls)
    total_tokens = sum(c.tokens_total for c in agent_calls)
    total_calls = len(agent_calls)

    models_used = list(set(c.model.value for c in agent_calls))
    phases_active = list(set(c.phase.value for c in agent_calls))

    # Calculate efficiency score (0-100)
    # Based on cost per token compared to average
    avg_cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
    efficiency_score = max(0, min(100, 100 - (avg_cost_per_token * 1000000)))  # Normalize

    return AgentCosts(
        agent_id=f"{project_id}:{agent_type.value}",
        agent_type=agent_type,
        project_id=project_id,
        total_cost=round(total_cost, 4),
        total_tokens=total_tokens,
        total_calls=total_calls,
        avg_cost_per_call=round(total_cost / total_calls, 4),
        avg_tokens_per_call=total_tokens // total_calls,
        models_used=models_used,
        phases_active=phases_active,
        first_call=min(c.timestamp for c in agent_calls),
        last_call=max(c.timestamp for c in agent_calls),
        efficiency_score=round(efficiency_score, 2)
    )


@router.post("/budget/{project_id}")
async def set_budget(project_id: str, budget_limit: float, alert_threshold: float = 0.75):
    """Set budget for a project"""
    budget = Budget(
        project_id=project_id,
        budget_limit=budget_limit,
        alert_threshold=alert_threshold
    )

    storage.set_budget(budget)

    return budget.model_dump(mode='json')


@router.get("/budget/{project_id}", response_model=BudgetStatus)
async def get_budget_status(project_id: str):
    """Get current budget status"""
    budget = storage.get_budget(project_id)

    if not budget:
        raise HTTPException(status_code=404, detail="No budget set for project")

    calls = storage.get_api_calls(project_id)
    current_spend = sum(c.cost for c in calls)

    remaining = budget.budget_limit - current_spend
    percentage_used = (current_spend / budget.budget_limit) * 100

    is_over_budget = current_spend > budget.budget_limit
    is_at_threshold = percentage_used >= (budget.alert_threshold * 100)

    # Project final cost based on current trend
    if len(calls) > 5:
        time_elapsed = (calls[-1].timestamp - calls[0].timestamp).total_seconds() / 3600  # hours
        if time_elapsed > 0:
            spend_rate = current_spend / time_elapsed
            # Assume project will take 2x current time (rough estimate)
            projected_final_cost = current_spend + (spend_rate * time_elapsed)
        else:
            projected_final_cost = None
    else:
        projected_final_cost = None

    return BudgetStatus(
        project_id=project_id,
        budget=budget,
        current_spend=round(current_spend, 4),
        remaining=round(remaining, 4),
        percentage_used=round(percentage_used, 2),
        is_over_budget=is_over_budget,
        is_at_threshold=is_at_threshold,
        projected_final_cost=round(projected_final_cost, 4) if projected_final_cost else None
    )


@router.get("/optimizations/{project_id}")
async def get_optimization_suggestions(project_id: str) -> List[OptimizationSuggestion]:
    """Get cost optimization suggestions"""
    calls = storage.get_api_calls(project_id)
    budget = storage.get_budget(project_id)

    if not calls:
        return []

    suggestions = optimizer.analyze_and_suggest(project_id, calls, budget)

    # Sort by priority and potential savings
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    suggestions.sort(
        key=lambda s: (priority_order.get(s.priority, 999), -s.potential_savings_pct)
    )

    return suggestions


@router.post("/estimate/{project_id}")
async def set_cost_estimate(project_id: str, estimated_cost: float):
    """Set estimated cost for a project"""
    storage.set_estimate(project_id, estimated_cost)

    return {
        "success": True,
        "project_id": project_id,
        "estimated_cost": estimated_cost
    }


@router.get("/comparison/{project_id}", response_model=CostComparison)
async def get_cost_comparison(project_id: str):
    """Compare estimated vs actual costs"""
    estimate = storage.get_estimate(project_id)
    calls = storage.get_api_calls(project_id)

    if not calls:
        raise HTTPException(status_code=404, detail="No cost data found")

    actual_cost = sum(c.cost for c in calls)

    if estimate:
        variance = actual_cost - estimate
        variance_pct = (variance / estimate) * 100 if estimate > 0 else 0
    else:
        estimate = 0
        variance = 0
        variance_pct = 0

    return CostComparison(
        project_id=project_id,
        estimated_cost=round(estimate, 4),
        actual_cost=round(actual_cost, 4),
        variance=round(variance, 4),
        variance_pct=round(variance_pct, 2)
    )


@router.get("/history/{project_id}")
async def get_cost_history(project_id: str, interval_minutes: int = 60) -> List[CostHistoryPoint]:
    """Get cost history over time"""
    calls = storage.get_api_calls(project_id)

    if not calls:
        return []

    # Sort by timestamp
    calls.sort(key=lambda c: c.timestamp)

    # Group by time intervals
    history = []
    start_time = calls[0].timestamp
    end_time = calls[-1].timestamp

    current_time = start_time
    interval = timedelta(minutes=interval_minutes)

    cumulative_cost = 0
    cumulative_tokens = 0
    cumulative_calls = 0
    call_index = 0

    while current_time <= end_time:
        # Add all calls up to current_time
        while call_index < len(calls) and calls[call_index].timestamp <= current_time:
            call = calls[call_index]
            cumulative_cost += call.cost
            cumulative_tokens += call.tokens_total
            cumulative_calls += 1
            call_index += 1

        if cumulative_calls > 0:
            history.append(CostHistoryPoint(
                timestamp=current_time,
                cumulative_cost=round(cumulative_cost, 4),
                tokens_used=cumulative_tokens,
                api_calls=cumulative_calls
            ))

        current_time += interval

    return history


@router.get("/models/pricing")
async def get_model_pricing():
    """Get current model pricing information"""
    return {
        "models": {
            model.value: {
                "input_per_1m": pricing["input"],
                "output_per_1m": pricing["output"],
                "avg_per_1m": (pricing["input"] + pricing["output"]) / 2
            }
            for model, pricing in MODEL_PRICING.items()
        },
        "currency": "USD",
        "unit": "per 1M tokens",
        "last_updated": "2025-10-27"
    }


@router.get("/health")
async def cost_tracking_health():
    """Health check for cost tracking system"""
    total_projects = len(storage.api_calls)
    total_calls = sum(len(calls) for calls in storage.api_calls.values())
    total_cost = sum(
        sum(c.cost for c in calls)
        for calls in storage.api_calls.values()
    )

    return {
        "status": "healthy",
        "total_projects": total_projects,
        "total_api_calls": total_calls,
        "total_cost_tracked": round(total_cost, 4),
        "active_budgets": len(storage.budgets),
        "models_supported": len(MODEL_PRICING)
    }
