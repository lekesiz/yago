"""
YAGO v8.0 - Model Registry
Central registry for all available AI models
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from .base import Model, ModelMetadata, ModelProvider, ModelCapability

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Central registry for AI models

    Responsibilities:
    - Register and discover models
    - Manage model metadata
    - Track model availability
    - Provide model selection
    """

    def __init__(self):
        """Initialize model registry"""
        self._models: Dict[str, Model] = {}  # model_id -> Model instance
        self._metadata: Dict[str, ModelMetadata] = {}  # model_id -> metadata

        logger.info("ModelRegistry initialized")

        # Register built-in models
        self._register_builtin_models()

    def register(self, model: Model) -> bool:
        """
        Register a model

        Args:
            model: Model instance

        Returns:
            True if registration successful
        """
        try:
            model_id = model.metadata.id

            if model_id in self._models:
                logger.warning(f"Model {model_id} already registered")
                return False

            self._models[model_id] = model
            self._metadata[model_id] = model.metadata

            logger.info(f"Model registered: {model_id}")
            return True

        except Exception as e:
            logger.error(f"Error registering model: {e}")
            return False

    def unregister(self, model_id: str) -> bool:
        """
        Unregister a model

        Args:
            model_id: Model ID

        Returns:
            True if unregistration successful
        """
        try:
            if model_id not in self._models:
                logger.warning(f"Model {model_id} not found")
                return False

            self._models.pop(model_id)
            self._metadata.pop(model_id)

            logger.info(f"Model unregistered: {model_id}")
            return True

        except Exception as e:
            logger.error(f"Error unregistering model: {e}")
            return False

    def get(self, model_id: str) -> Optional[Model]:
        """Get model by ID"""
        return self._models.get(model_id)

    def get_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID"""
        return self._metadata.get(model_id)

    def list_models(
        self,
        provider: Optional[ModelProvider] = None,
        capability: Optional[ModelCapability] = None,
        exclude_deprecated: bool = True
    ) -> List[ModelMetadata]:
        """
        List models with optional filters

        Args:
            provider: Filter by provider
            capability: Filter by capability
            exclude_deprecated: Exclude deprecated models

        Returns:
            List of model metadata
        """
        models = list(self._metadata.values())

        # Filter by provider
        if provider:
            models = [m for m in models if m.provider == provider]

        # Filter by capability
        if capability:
            models = [m for m in models if capability in m.capabilities]

        # Exclude deprecated
        if exclude_deprecated:
            models = [m for m in models if not m.is_deprecated]

        return models

    def search(
        self,
        query: str,
        provider: Optional[ModelProvider] = None
    ) -> List[ModelMetadata]:
        """
        Search models by name or description

        Args:
            query: Search query
            provider: Optional provider filter

        Returns:
            List of matching models
        """
        query_lower = query.lower()
        results = []

        for metadata in self._metadata.values():
            # Filter by provider if specified
            if provider and metadata.provider != provider:
                continue

            # Search in name and description
            if (query_lower in metadata.name.lower() or
                (metadata.description and query_lower in metadata.description.lower())):
                results.append(metadata)

        return results

    def get_best_model(
        self,
        capability: ModelCapability,
        max_cost: Optional[float] = None,
        min_context_window: Optional[int] = None
    ) -> Optional[ModelMetadata]:
        """
        Get the best model for a capability

        Args:
            capability: Required capability
            max_cost: Maximum cost per 1M tokens (input + output)
            min_context_window: Minimum context window

        Returns:
            Best matching model metadata
        """
        # Get models with capability
        models = [
            m for m in self._metadata.values()
            if capability in m.capabilities and not m.is_deprecated
        ]

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

        if not models:
            return None

        # Sort by quality/cost ratio (simple heuristic)
        # Prefer larger context window and lower cost
        models.sort(
            key=lambda m: (
                -m.context_window,  # Higher is better
                m.input_price_per_1m + m.output_price_per_1m  # Lower is better
            )
        )

        return models[0]

    def get_cheapest_model(
        self,
        capability: Optional[ModelCapability] = None
    ) -> Optional[ModelMetadata]:
        """
        Get the cheapest model

        Args:
            capability: Optional capability filter

        Returns:
            Cheapest model metadata
        """
        models = list(self._metadata.values())

        # Filter by capability
        if capability:
            models = [m for m in models if capability in m.capabilities]

        # Exclude deprecated
        models = [m for m in models if not m.is_deprecated]

        if not models:
            return None

        # Sort by total cost
        models.sort(key=lambda m: m.input_price_per_1m + m.output_price_per_1m)

        return models[0]

    def get_fastest_model(
        self,
        capability: Optional[ModelCapability] = None
    ) -> Optional[ModelMetadata]:
        """
        Get the fastest model

        Args:
            capability: Optional capability filter

        Returns:
            Fastest model metadata
        """
        models = list(self._metadata.values())

        # Filter by capability
        if capability:
            models = [m for m in models if capability in m.capabilities]

        # Exclude deprecated
        models = [m for m in models if not m.is_deprecated]

        # Filter models with latency data
        models = [m for m in models if m.average_latency_ms is not None]

        if not models:
            return None

        # Sort by latency
        models.sort(key=lambda m: m.average_latency_ms)

        return models[0]

    def get_stats(self) -> Dict[str, any]:
        """Get registry statistics"""
        models = list(self._metadata.values())

        return {
            "total_models": len(models),
            "by_provider": {
                provider.value: len([
                    m for m in models if m.provider == provider
                ])
                for provider in ModelProvider
            },
            "deprecated_count": len([m for m in models if m.is_deprecated]),
            "active_count": len([m for m in models if not m.is_deprecated])
        }

    def _register_builtin_models(self):
        """Register built-in model metadata"""

        # OpenAI Models
        openai_models = [
            ModelMetadata(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider=ModelProvider.OPENAI,
                version="turbo-2024-04-09",
                description="Most capable GPT-4 model with 128K context",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.VISION,
                    ModelCapability.STREAMING,
                    ModelCapability.JSON_MODE
                ],
                max_tokens=4096,
                context_window=128000,
                supports_streaming=True,
                supports_functions=True,
                supports_vision=True,
                input_price_per_1m=10.0,
                output_price_per_1m=30.0,
                average_latency_ms=1500.0,
                tokens_per_second=50.0
            ),
            ModelMetadata(
                id="gpt-4",
                name="GPT-4",
                provider=ModelProvider.OPENAI,
                version="0613",
                description="Original GPT-4 model with 8K context",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING
                ],
                max_tokens=4096,
                context_window=8192,
                supports_streaming=True,
                supports_functions=True,
                input_price_per_1m=30.0,
                output_price_per_1m=60.0,
                average_latency_ms=2000.0
            ),
            ModelMetadata(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider=ModelProvider.OPENAI,
                version="0125",
                description="Fast and economical model",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING,
                    ModelCapability.JSON_MODE
                ],
                max_tokens=4096,
                context_window=16385,
                supports_streaming=True,
                supports_functions=True,
                input_price_per_1m=0.5,
                output_price_per_1m=1.5,
                average_latency_ms=800.0,
                tokens_per_second=80.0
            )
        ]

        # Anthropic Models
        anthropic_models = [
            ModelMetadata(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider=ModelProvider.ANTHROPIC,
                version="20240229",
                description="Most capable Claude model",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.VISION,
                    ModelCapability.STREAMING
                ],
                max_tokens=4096,
                context_window=200000,
                supports_streaming=True,
                supports_vision=True,
                input_price_per_1m=15.0,
                output_price_per_1m=75.0,
                average_latency_ms=1800.0
            ),
            ModelMetadata(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider=ModelProvider.ANTHROPIC,
                version="20240229",
                description="Balanced performance and cost",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.VISION,
                    ModelCapability.STREAMING
                ],
                max_tokens=4096,
                context_window=200000,
                supports_streaming=True,
                supports_vision=True,
                input_price_per_1m=3.0,
                output_price_per_1m=15.0,
                average_latency_ms=1200.0,
                tokens_per_second=60.0
            ),
            ModelMetadata(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                provider=ModelProvider.ANTHROPIC,
                version="20240307",
                description="Fast and cost-effective",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.VISION,
                    ModelCapability.STREAMING
                ],
                max_tokens=4096,
                context_window=200000,
                supports_streaming=True,
                supports_vision=True,
                input_price_per_1m=0.25,
                output_price_per_1m=1.25,
                average_latency_ms=600.0,
                tokens_per_second=100.0
            )
        ]

        # Google Models
        google_models = [
            ModelMetadata(
                id="gemini-pro",
                name="Gemini Pro",
                provider=ModelProvider.GOOGLE,
                version="1.0",
                description="Google's flagship model",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.STREAMING
                ],
                max_tokens=8192,
                context_window=32768,
                supports_streaming=True,
                input_price_per_1m=0.5,
                output_price_per_1m=1.5,
                average_latency_ms=1000.0
            )
        ]

        # Register all models
        for metadata in openai_models + anthropic_models + google_models:
            self._metadata[metadata.id] = metadata

        logger.info(f"Registered {len(self._metadata)} built-in models")


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Get the global model registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
