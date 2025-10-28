"""
YAGO v8.0 - Model Base Classes
Base classes and interfaces for AI models
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, AsyncIterator
from pydantic import BaseModel, Field
from datetime import datetime


class ModelProvider(str, Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    CUSTOM = "custom"


class ModelCapability(str, Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_UNDERSTANDING = "image_understanding"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    VISION = "vision"


class ModelMetadata(BaseModel):
    """Metadata for an AI model"""

    # Basic info
    id: str
    name: str
    provider: ModelProvider
    version: str
    description: Optional[str] = None

    # Capabilities
    capabilities: List[ModelCapability] = Field(default_factory=list)

    # Specifications
    max_tokens: int = 4096
    context_window: int = 4096
    supports_streaming: bool = True
    supports_functions: bool = False
    supports_vision: bool = False

    # Pricing (per 1M tokens)
    input_price_per_1m: float = 0.0
    output_price_per_1m: float = 0.0

    # Performance
    average_latency_ms: Optional[float] = None
    tokens_per_second: Optional[float] = None

    # Metadata
    release_date: Optional[datetime] = None
    is_deprecated: bool = False
    deprecated_date: Optional[datetime] = None
    replacement_model: Optional[str] = None

    # Configuration
    default_temperature: float = 0.7
    default_max_tokens: int = 1024
    default_top_p: float = 1.0

    # Custom fields
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "openai",
                "version": "turbo-2024-04-09",
                "max_tokens": 128000,
                "context_window": 128000,
                "input_price_per_1m": 10.0,
                "output_price_per_1m": 30.0
            }
        }


class ModelRequest(BaseModel):
    """Request to a model"""

    # Content
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    prompt: Optional[str] = None

    # Parameters
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Special features
    stream: bool = False
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[str] = None
    response_format: Optional[Dict[str, str]] = None

    # Metadata
    user: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel):
    """Response from a model"""

    # Content
    content: str
    role: str = "assistant"

    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Cost
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0

    # Performance
    latency_ms: float = 0.0
    tokens_per_second: float = 0.0

    # Metadata
    model_id: str
    finish_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Function calling
    function_call: Optional[Dict[str, Any]] = None

    # Custom fields
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Model(ABC):
    """
    Abstract base class for AI models

    All model adapters must implement this interface
    """

    def __init__(self, metadata: ModelMetadata, api_key: Optional[str] = None):
        """Initialize model"""
        self.metadata = metadata
        self.api_key = api_key
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the model

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """
        Generate a response

        Args:
            request: Model request

        Returns:
            Model response
        """
        pass

    @abstractmethod
    async def generate_stream(self, request: ModelRequest) -> AsyncIterator[str]:
        """
        Generate a streaming response

        Args:
            request: Model request

        Yields:
            Response chunks
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text

        Args:
            text: Text to count

        Returns:
            Token count
        """
        pass

    async def validate_request(self, request: ModelRequest) -> bool:
        """
        Validate a request

        Args:
            request: Request to validate

        Returns:
            True if valid
        """
        # Check token limits
        if request.max_tokens > self.metadata.max_tokens:
            return False

        # Check capabilities
        if request.stream and not self.metadata.supports_streaming:
            return False

        if request.functions and not self.metadata.supports_functions:
            return False

        return True

    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, float]:
        """
        Calculate cost for token usage

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Dict with input_cost, output_cost, total_cost
        """
        input_cost = (prompt_tokens / 1_000_000) * self.metadata.input_price_per_1m
        output_cost = (completion_tokens / 1_000_000) * self.metadata.output_price_per_1m
        total_cost = input_cost + output_cost

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        }

    def get_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "provider": self.metadata.provider.value,
            "version": self.metadata.version,
            "capabilities": [c.value for c in self.metadata.capabilities],
            "max_tokens": self.metadata.max_tokens,
            "context_window": self.metadata.context_window,
            "pricing": {
                "input_per_1m": self.metadata.input_price_per_1m,
                "output_per_1m": self.metadata.output_price_per_1m
            },
            "supports_streaming": self.metadata.supports_streaming,
            "supports_functions": self.metadata.supports_functions,
            "supports_vision": self.metadata.supports_vision,
            "is_deprecated": self.metadata.is_deprecated
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check model health"""
        return {
            "model_id": self.metadata.id,
            "initialized": self._initialized,
            "healthy": self._initialized,
            "timestamp": datetime.utcnow().isoformat()
        }
