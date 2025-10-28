"""
YAGO v8.0 - Models Management API
RESTful API for AI model management and selection
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from yago.models import (
    get_registry,
    ModelSelector,
    ModelComparison,
    ModelProvider,
    ModelCapability,
    ModelRequest,
    SelectionStrategy
)
from yago.models.adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GoogleAdapter,
    LocalAdapter
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/models", tags=["Models"])

# Initialize components
registry = get_registry()
selector = ModelSelector(registry)
comparison = ModelComparison(registry)


# Request/Response Models

class ModelListRequest(BaseModel):
    """Request to list models"""
    provider: Optional[str] = None
    capability: Optional[str] = None
    exclude_deprecated: bool = True


class ModelSelectionRequest(BaseModel):
    """Request to select best model"""
    strategy: str = "balanced"
    capability: Optional[str] = None
    provider: Optional[str] = None
    max_cost: Optional[float] = None
    min_context_window: Optional[int] = None
    max_latency_ms: Optional[float] = None
    custom_weights: Optional[Dict[str, float]] = None


class ModelGenerateRequest(BaseModel):
    """Request to generate with a model"""
    model_id: str
    messages: List[Dict[str, Any]] = []
    prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False


class ModelCompareRequest(BaseModel):
    """Request to compare models"""
    model_ids: List[str]
    messages: List[Dict[str, Any]] = []
    prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: float = 30.0


class ModelBenchmarkRequest(BaseModel):
    """Request to benchmark a model"""
    model_id: str
    test_cases: List[Dict[str, Any]]
    iterations: int = 1


# Endpoints

@router.get("/list")
async def list_models(
    provider: Optional[str] = None,
    capability: Optional[str] = None,
    exclude_deprecated: bool = True
):
    """
    List available models

    Args:
        provider: Filter by provider (openai, anthropic, google, etc.)
        capability: Filter by capability
        exclude_deprecated: Exclude deprecated models

    Returns:
        List of models
    """
    try:
        # Parse filters
        provider_filter = ModelProvider(provider) if provider else None
        capability_filter = ModelCapability(capability) if capability else None

        # Get models
        models = registry.list_models(
            provider=provider_filter,
            capability=capability_filter,
            exclude_deprecated=exclude_deprecated
        )

        return {
            "total": len(models),
            "models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "provider": m.provider.value,
                    "version": m.version,
                    "description": m.description,
                    "capabilities": [c.value for c in m.capabilities],
                    "context_window": m.context_window,
                    "max_tokens": m.max_tokens,
                    "pricing": {
                        "input_per_1m": m.input_price_per_1m,
                        "output_per_1m": m.output_price_per_1m
                    },
                    "supports_streaming": m.supports_streaming,
                    "supports_functions": m.supports_functions,
                    "supports_vision": m.supports_vision,
                    "is_deprecated": m.is_deprecated
                }
                for m in models
            ]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filter value: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )


@router.get("/{model_id}")
async def get_model(model_id: str):
    """
    Get model details

    Args:
        model_id: Model ID

    Returns:
        Model information
    """
    try:
        metadata = registry.get_metadata(model_id)

        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )

        return {
            "id": metadata.id,
            "name": metadata.name,
            "provider": metadata.provider.value,
            "version": metadata.version,
            "description": metadata.description,
            "capabilities": [c.value for c in metadata.capabilities],
            "specifications": {
                "max_tokens": metadata.max_tokens,
                "context_window": metadata.context_window,
                "supports_streaming": metadata.supports_streaming,
                "supports_functions": metadata.supports_functions,
                "supports_vision": metadata.supports_vision
            },
            "pricing": {
                "input_per_1m": metadata.input_price_per_1m,
                "output_per_1m": metadata.output_price_per_1m
            },
            "performance": {
                "average_latency_ms": metadata.average_latency_ms,
                "tokens_per_second": metadata.tokens_per_second
            },
            "defaults": {
                "temperature": metadata.default_temperature,
                "max_tokens": metadata.default_max_tokens,
                "top_p": metadata.default_top_p
            },
            "is_deprecated": metadata.is_deprecated,
            "release_date": metadata.release_date.isoformat() if metadata.release_date else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model {model_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model"
        )


@router.post("/select")
async def select_model(request: ModelSelectionRequest):
    """
    Select best model based on criteria

    Args:
        request: Selection criteria

    Returns:
        Selected model ID and info
    """
    try:
        # Parse strategy
        try:
            strategy = SelectionStrategy(request.strategy)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid strategy: {request.strategy}"
            )

        # Parse filters
        capability = ModelCapability(request.capability) if request.capability else None
        provider = ModelProvider(request.provider) if request.provider else None

        # Select model
        model_id = selector.select(
            strategy=strategy,
            capability=capability,
            provider=provider,
            max_cost=request.max_cost,
            min_context_window=request.min_context_window,
            max_latency_ms=request.max_latency_ms,
            custom_weights=request.custom_weights
        )

        if not model_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No model matches the criteria"
            )

        # Get model info
        metadata = registry.get_metadata(model_id)

        # Get fallback options
        fallbacks = selector.get_fallback_models(model_id, max_fallbacks=3)

        return {
            "selected_model": model_id,
            "strategy": request.strategy,
            "model_info": {
                "name": metadata.name,
                "provider": metadata.provider.value,
                "context_window": metadata.context_window,
                "cost_per_1m": metadata.input_price_per_1m + metadata.output_price_per_1m
            },
            "fallback_models": fallbacks
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to select model"
        )


@router.post("/compare")
async def compare_models(request: ModelCompareRequest):
    """
    Compare multiple models with same prompt

    Args:
        request: Comparison request

    Returns:
        Comparison results
    """
    try:
        # Build model request
        model_request = ModelRequest(
            messages=request.messages,
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Run comparison
        results = await comparison.compare(
            model_ids=request.model_ids,
            request=model_request,
            timeout=request.timeout
        )

        return results

    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare models: {str(e)}"
        )


@router.post("/benchmark")
async def benchmark_model(request: ModelBenchmarkRequest):
    """
    Benchmark a model

    Args:
        request: Benchmark request

    Returns:
        Benchmark results
    """
    try:
        # Build test cases
        test_cases = []
        for test in request.test_cases:
            test_cases.append(ModelRequest(**test))

        # Run benchmark
        results = await comparison.benchmark(
            model_id=request.model_id,
            test_cases=test_cases,
            iterations=request.iterations
        )

        return results

    except Exception as e:
        logger.error(f"Error benchmarking model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to benchmark model: {str(e)}"
        )


@router.get("/search")
async def search_models(
    query: str,
    provider: Optional[str] = None
):
    """
    Search models by name or description

    Args:
        query: Search query
        provider: Optional provider filter

    Returns:
        Matching models
    """
    try:
        provider_filter = ModelProvider(provider) if provider else None

        models = registry.search(query, provider_filter)

        return {
            "query": query,
            "total": len(models),
            "models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "provider": m.provider.value,
                    "description": m.description
                }
                for m in models
            ]
        }

    except Exception as e:
        logger.error(f"Error searching models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search models"
        )


@router.get("/providers")
async def list_providers():
    """List available providers"""
    return {
        "providers": [
            {
                "id": p.value,
                "name": p.value.title()
            }
            for p in ModelProvider
        ]
    }


@router.get("/capabilities")
async def list_capabilities():
    """List available capabilities"""
    return {
        "capabilities": [
            {
                "id": c.value,
                "name": c.value.replace("_", " ").title()
            }
            for c in ModelCapability
        ]
    }


@router.get("/strategies")
async def list_strategies():
    """List available selection strategies"""
    return {
        "strategies": [
            {
                "id": s.value,
                "name": s.value.replace("_", " ").title(),
                "description": {
                    "cheapest": "Select the most cost-effective model",
                    "fastest": "Select the model with lowest latency",
                    "best_quality": "Select the highest quality model",
                    "balanced": "Balance cost, speed, and quality",
                    "custom": "Use custom weights for selection"
                }.get(s.value, "")
            }
            for s in SelectionStrategy
        ]
    }


@router.get("/stats")
async def get_stats():
    """Get registry statistics"""
    try:
        stats = registry.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.get("/recommendations/{capability}")
async def get_recommendations(
    capability: str,
    max_cost: Optional[float] = None
):
    """
    Get recommended models for a capability

    Args:
        capability: Required capability
        max_cost: Optional max cost constraint

    Returns:
        Recommended models
    """
    try:
        cap = ModelCapability(capability)

        recommendations = {
            "cheapest": registry.get_cheapest_model(cap),
            "fastest": registry.get_fastest_model(cap),
            "best": registry.get_best_model(
                capability=cap,
                max_cost=max_cost
            )
        }

        return {
            "capability": capability,
            "recommendations": {
                k: {
                    "id": v.id,
                    "name": v.name,
                    "provider": v.provider.value,
                    "cost_per_1m": v.input_price_per_1m + v.output_price_per_1m
                } if v else None
                for k, v in recommendations.items()
            }
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid capability: {capability}"
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


# Export router
models_router = router
