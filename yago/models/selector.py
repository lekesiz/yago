"""
YAGO v8.0 - Model Selector
Intelligent model selection based on requirements
"""

import logging
from typing import Optional, List, Dict, Any
from enum import Enum

from .base import ModelCapability, ModelProvider
from .registry import ModelRegistry, get_registry

logger = logging.getLogger(__name__)


class SelectionStrategy(str, Enum):
    """Model selection strategies"""
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    BEST_QUALITY = "best_quality"
    BALANCED = "balanced"
    CUSTOM = "custom"


class ModelSelector:
    """
    Intelligent model selection

    Responsibilities:
    - Select best model based on requirements
    - Apply selection strategies
    - Handle fallback options
    """

    def __init__(self, registry: Optional[ModelRegistry] = None):
        """Initialize model selector"""
        self.registry = registry or get_registry()

    def select(
        self,
        strategy: SelectionStrategy = SelectionStrategy.BALANCED,
        capability: Optional[ModelCapability] = None,
        provider: Optional[ModelProvider] = None,
        max_cost: Optional[float] = None,
        min_context_window: Optional[int] = None,
        max_latency_ms: Optional[float] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Optional[str]:
        """
        Select best model based on criteria

        Args:
            strategy: Selection strategy
            capability: Required capability
            provider: Preferred provider
            max_cost: Maximum cost per 1M tokens
            min_context_window: Minimum context window
            max_latency_ms: Maximum latency in milliseconds
            custom_weights: Custom weights for scoring

        Returns:
            Selected model ID
        """
        try:
            # Get available models
            models = self.registry.list_models(
                provider=provider,
                capability=capability,
                exclude_deprecated=True
            )

            if not models:
                logger.warning("No models available for selection")
                return None

            # Apply filters
            if max_cost:
                models = [
                    m for m in models
                    if (m.input_price_per_1m + m.output_price_per_1m) <= max_cost
                ]

            if min_context_window:
                models = [
                    m for m in models
                    if m.context_window >= min_context_window
                ]

            if max_latency_ms:
                models = [
                    m for m in models
                    if m.average_latency_ms and m.average_latency_ms <= max_latency_ms
                ]

            if not models:
                logger.warning("No models match the criteria")
                return None

            # Apply strategy
            if strategy == SelectionStrategy.CHEAPEST:
                selected = self._select_cheapest(models)
            elif strategy == SelectionStrategy.FASTEST:
                selected = self._select_fastest(models)
            elif strategy == SelectionStrategy.BEST_QUALITY:
                selected = self._select_best_quality(models)
            elif strategy == SelectionStrategy.BALANCED:
                selected = self._select_balanced(models)
            elif strategy == SelectionStrategy.CUSTOM and custom_weights:
                selected = self._select_custom(models, custom_weights)
            else:
                selected = self._select_balanced(models)

            if selected:
                logger.info(f"Selected model: {selected.id} (strategy: {strategy.value})")
                return selected.id

            return None

        except Exception as e:
            logger.error(f"Error selecting model: {e}")
            return None

    def _select_cheapest(self, models):
        """Select cheapest model"""
        models = sorted(
            models,
            key=lambda m: m.input_price_per_1m + m.output_price_per_1m
        )
        return models[0] if models else None

    def _select_fastest(self, models):
        """Select fastest model"""
        # Filter models with latency data
        models_with_latency = [m for m in models if m.average_latency_ms]

        if not models_with_latency:
            return models[0] if models else None

        models_with_latency = sorted(
            models_with_latency,
            key=lambda m: m.average_latency_ms
        )
        return models_with_latency[0]

    def _select_best_quality(self, models):
        """Select highest quality model (by context window and capabilities)"""
        models = sorted(
            models,
            key=lambda m: (
                -m.context_window,  # Larger context is better
                -len(m.capabilities),  # More capabilities is better
                m.input_price_per_1m + m.output_price_per_1m  # Lower cost is better (tie-breaker)
            )
        )
        return models[0] if models else None

    def _select_balanced(self, models):
        """Select balanced model (quality/cost/speed)"""
        # Score each model
        scored_models = []

        for model in models:
            score = self._calculate_balanced_score(model)
            scored_models.append((model, score))

        # Sort by score (higher is better)
        scored_models.sort(key=lambda x: x[1], reverse=True)

        return scored_models[0][0] if scored_models else None

    def _calculate_balanced_score(self, model) -> float:
        """Calculate balanced score for a model"""
        # Normalize metrics to 0-1 range

        # Cost score (lower is better, so invert)
        total_cost = model.input_price_per_1m + model.output_price_per_1m
        cost_score = 1.0 / (1.0 + total_cost / 10.0)  # Normalize around $10/1M

        # Context window score (higher is better)
        context_score = min(model.context_window / 100000, 1.0)  # Normalize to 100K

        # Speed score (lower latency is better)
        if model.average_latency_ms:
            speed_score = 1.0 / (1.0 + model.average_latency_ms / 1000.0)  # Normalize around 1s
        else:
            speed_score = 0.5  # Default for unknown

        # Capability score
        capability_score = len(model.capabilities) / 10.0  # Normalize to 10 capabilities

        # Weighted average
        score = (
            cost_score * 0.3 +
            context_score * 0.3 +
            speed_score * 0.2 +
            capability_score * 0.2
        )

        return score

    def _select_custom(self, models, weights: Dict[str, float]):
        """Select model using custom weights"""
        scored_models = []

        for model in models:
            score = 0.0

            # Cost component
            if "cost" in weights:
                total_cost = model.input_price_per_1m + model.output_price_per_1m
                cost_score = 1.0 / (1.0 + total_cost / 10.0)
                score += cost_score * weights["cost"]

            # Speed component
            if "speed" in weights and model.average_latency_ms:
                speed_score = 1.0 / (1.0 + model.average_latency_ms / 1000.0)
                score += speed_score * weights["speed"]

            # Context component
            if "context" in weights:
                context_score = min(model.context_window / 100000, 1.0)
                score += context_score * weights["context"]

            # Capability component
            if "capability" in weights:
                capability_score = len(model.capabilities) / 10.0
                score += capability_score * weights["capability"]

            scored_models.append((model, score))

        # Sort by score
        scored_models.sort(key=lambda x: x[1], reverse=True)

        return scored_models[0][0] if scored_models else None

    def get_fallback_models(
        self,
        primary_model_id: str,
        max_fallbacks: int = 3
    ) -> List[str]:
        """
        Get fallback models for a primary model

        Args:
            primary_model_id: Primary model ID
            max_fallbacks: Maximum number of fallbacks

        Returns:
            List of fallback model IDs
        """
        try:
            primary = self.registry.get_metadata(primary_model_id)
            if not primary:
                return []

            # Get models with similar capabilities
            candidates = self.registry.list_models(
                provider=None,
                capability=None,
                exclude_deprecated=True
            )

            # Filter out primary model
            candidates = [m for m in candidates if m.id != primary_model_id]

            # Score by similarity
            scored = []
            for candidate in candidates:
                similarity = self._calculate_similarity(primary, candidate)
                scored.append((candidate.id, similarity))

            # Sort by similarity
            scored.sort(key=lambda x: x[1], reverse=True)

            # Return top fallbacks
            return [model_id for model_id, _ in scored[:max_fallbacks]]

        except Exception as e:
            logger.error(f"Error getting fallback models: {e}")
            return []

    def _calculate_similarity(self, model1, model2) -> float:
        """Calculate similarity between two models"""
        score = 0.0

        # Same provider: +0.3
        if model1.provider == model2.provider:
            score += 0.3

        # Similar capabilities: +0.4
        common_caps = set(model1.capabilities) & set(model2.capabilities)
        if model1.capabilities:
            score += 0.4 * (len(common_caps) / len(model1.capabilities))

        # Similar context window: +0.2
        if model1.context_window > 0:
            ratio = min(model2.context_window, model1.context_window) / max(model2.context_window, model1.context_window)
            score += 0.2 * ratio

        # Similar cost: +0.1
        cost1 = model1.input_price_per_1m + model1.output_price_per_1m
        cost2 = model2.input_price_per_1m + model2.output_price_per_1m
        if cost1 > 0:
            ratio = min(cost2, cost1) / max(cost2, cost1)
            score += 0.1 * ratio

        return score
