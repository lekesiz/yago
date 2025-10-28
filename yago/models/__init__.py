"""
YAGO v8.0 - AI Model Management
Dynamic model selection and management system
"""

from .registry import ModelRegistry, get_registry
from .base import (
    ModelProvider,
    ModelCapability,
    ModelMetadata,
    Model,
)
from .adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GoogleAdapter,
    LocalAdapter,
)
from .selector import ModelSelector
from .comparison import ModelComparison

__all__ = [
    # Registry
    'ModelRegistry',
    'get_registry',

    # Base
    'ModelProvider',
    'ModelCapability',
    'ModelMetadata',
    'Model',

    # Adapters
    'OpenAIAdapter',
    'AnthropicAdapter',
    'GoogleAdapter',
    'LocalAdapter',

    # Selection
    'ModelSelector',
    'ModelComparison',
]
