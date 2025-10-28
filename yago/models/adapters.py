"""
YAGO v8.0 - Model Adapters
Adapters for different AI model providers
"""

import time
import logging
from typing import AsyncIterator, Optional
from datetime import datetime

from .base import Model, ModelRequest, ModelResponse, ModelMetadata

logger = logging.getLogger(__name__)


class OpenAIAdapter(Model):
    """Adapter for OpenAI models"""

    def __init__(self, metadata: ModelMetadata, api_key: str):
        super().__init__(metadata, api_key)
        self.client = None

    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            self._initialized = True
            logger.info(f"OpenAI model initialized: {self.metadata.id}")
            return True
        except Exception as e:
            logger.error(f"Error initializing OpenAI model: {e}")
            return False

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using OpenAI"""
        if not self._initialized:
            await self.initialize()

        try:
            start_time = time.time()

            # Prepare parameters
            params = {
                "model": self.metadata.id,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "top_p": request.top_p,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty,
            }

            # Add optional parameters
            if request.functions:
                params["functions"] = request.functions
            if request.function_call:
                params["function_call"] = request.function_call
            if request.response_format:
                params["response_format"] = request.response_format
            if request.user:
                params["user"] = request.user

            # Make API call
            response = await self.client.chat.completions.create(**params)

            latency_ms = (time.time() - start_time) * 1000

            # Extract response data
            choice = response.choices[0]
            message = choice.message

            # Calculate costs
            costs = self.calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )

            # Build response
            model_response = ModelResponse(
                content=message.content or "",
                role=message.role,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                input_cost=costs["input_cost"],
                output_cost=costs["output_cost"],
                total_cost=costs["total_cost"],
                latency_ms=latency_ms,
                tokens_per_second=response.usage.completion_tokens / (latency_ms / 1000) if latency_ms > 0 else 0,
                model_id=self.metadata.id,
                finish_reason=choice.finish_reason,
                function_call=message.function_call.model_dump() if message.function_call else None
            )

            return model_response

        except Exception as e:
            logger.error(f"Error generating with OpenAI: {e}")
            raise

    async def generate_stream(self, request: ModelRequest) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI"""
        if not self._initialized:
            await self.initialize()

        try:
            # Prepare parameters
            params = {
                "model": self.metadata.id,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "top_p": request.top_p,
                "stream": True
            }

            # Stream response
            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error streaming with OpenAI: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        try:
            import tiktoken

            # Get encoding for model
            if "gpt-4" in self.metadata.id:
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif "gpt-3.5" in self.metadata.id:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                encoding = tiktoken.get_encoding("cl100k_base")

            return len(encoding.encode(text))

        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimate
            return len(text) // 4


class AnthropicAdapter(Model):
    """Adapter for Anthropic Claude models"""

    def __init__(self, metadata: ModelMetadata, api_key: str):
        super().__init__(metadata, api_key)
        self.client = None

    async def initialize(self) -> bool:
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            self._initialized = True
            logger.info(f"Anthropic model initialized: {self.metadata.id}")
            return True
        except Exception as e:
            logger.error(f"Error initializing Anthropic model: {e}")
            return False

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Anthropic"""
        if not self._initialized:
            await self.initialize()

        try:
            start_time = time.time()

            # Convert messages format
            system_message = None
            messages = []

            for msg in request.messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    messages.append(msg)

            # Make API call
            response = await self.client.messages.create(
                model=self.metadata.id,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                messages=messages,
                system=system_message
            )

            latency_ms = (time.time() - start_time) * 1000

            # Calculate costs
            costs = self.calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            # Build response
            model_response = ModelResponse(
                content=response.content[0].text,
                role="assistant",
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                input_cost=costs["input_cost"],
                output_cost=costs["output_cost"],
                total_cost=costs["total_cost"],
                latency_ms=latency_ms,
                tokens_per_second=response.usage.output_tokens / (latency_ms / 1000) if latency_ms > 0 else 0,
                model_id=self.metadata.id,
                finish_reason=response.stop_reason
            )

            return model_response

        except Exception as e:
            logger.error(f"Error generating with Anthropic: {e}")
            raise

    async def generate_stream(self, request: ModelRequest) -> AsyncIterator[str]:
        """Generate streaming response using Anthropic"""
        if not self._initialized:
            await self.initialize()

        try:
            # Convert messages format
            system_message = None
            messages = []

            for msg in request.messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    messages.append(msg)

            # Stream response
            async with self.client.messages.stream(
                model=self.metadata.id,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=messages,
                system=system_message
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Error streaming with Anthropic: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens using Anthropic's tokenizer"""
        try:
            count = await self.client.count_tokens(text)
            return count
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback: rough estimate
            return len(text) // 4


class GoogleAdapter(Model):
    """Adapter for Google Gemini models"""

    def __init__(self, metadata: ModelMetadata, api_key: str):
        super().__init__(metadata, api_key)
        self.client = None

    async def initialize(self) -> bool:
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.metadata.id)
            self._initialized = True
            logger.info(f"Google model initialized: {self.metadata.id}")
            return True
        except Exception as e:
            logger.error(f"Error initializing Google model: {e}")
            return False

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Google Gemini"""
        if not self._initialized:
            await self.initialize()

        try:
            start_time = time.time()

            # Convert messages to prompt
            prompt = "\n\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in request.messages
            ])

            # Make API call
            response = await self.client.generate_content_async(
                prompt,
                generation_config={
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "max_output_tokens": request.max_tokens,
                }
            )

            latency_ms = (time.time() - start_time) * 1000

            # Estimate token counts (Google doesn't provide exact counts)
            prompt_tokens = await self.count_tokens(prompt)
            completion_tokens = await self.count_tokens(response.text)

            # Calculate costs
            costs = self.calculate_cost(prompt_tokens, completion_tokens)

            # Build response
            model_response = ModelResponse(
                content=response.text,
                role="assistant",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                input_cost=costs["input_cost"],
                output_cost=costs["output_cost"],
                total_cost=costs["total_cost"],
                latency_ms=latency_ms,
                tokens_per_second=completion_tokens / (latency_ms / 1000) if latency_ms > 0 else 0,
                model_id=self.metadata.id
            )

            return model_response

        except Exception as e:
            logger.error(f"Error generating with Google: {e}")
            raise

    async def generate_stream(self, request: ModelRequest) -> AsyncIterator[str]:
        """Generate streaming response using Google Gemini"""
        if not self._initialized:
            await self.initialize()

        try:
            # Convert messages to prompt
            prompt = "\n\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in request.messages
            ])

            # Stream response
            response = await self.client.generate_content_async(
                prompt,
                stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Error streaming with Google: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens"""
        try:
            # Google Gemini uses different tokenization
            # Fallback to character-based estimation
            return len(text) // 4
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return len(text) // 4


class LocalAdapter(Model):
    """Adapter for local models (Ollama, LM Studio, etc.)"""

    def __init__(self, metadata: ModelMetadata, base_url: str = "http://localhost:11434"):
        super().__init__(metadata, None)
        self.base_url = base_url
        self.client = None

    async def initialize(self) -> bool:
        """Initialize local model client"""
        try:
            import httpx
            self.client = httpx.AsyncClient(base_url=self.base_url)
            self._initialized = True
            logger.info(f"Local model initialized: {self.metadata.id}")
            return True
        except Exception as e:
            logger.error(f"Error initializing local model: {e}")
            return False

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using local model"""
        if not self._initialized:
            await self.initialize()

        try:
            start_time = time.time()

            # Make API call to local server (Ollama format)
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.metadata.id,
                    "prompt": request.messages[-1]["content"] if request.messages else request.prompt,
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "stream": False
                }
            )

            latency_ms = (time.time() - start_time) * 1000

            result = response.json()
            content = result.get("response", "")

            # Estimate tokens (no exact count from local models)
            prompt_tokens = await self.count_tokens(request.messages[-1]["content"] if request.messages else request.prompt or "")
            completion_tokens = await self.count_tokens(content)

            # Local models have no cost
            model_response = ModelResponse(
                content=content,
                role="assistant",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                input_cost=0.0,
                output_cost=0.0,
                total_cost=0.0,
                latency_ms=latency_ms,
                tokens_per_second=completion_tokens / (latency_ms / 1000) if latency_ms > 0 else 0,
                model_id=self.metadata.id
            )

            return model_response

        except Exception as e:
            logger.error(f"Error generating with local model: {e}")
            raise

    async def generate_stream(self, request: ModelRequest) -> AsyncIterator[str]:
        """Generate streaming response using local model"""
        if not self._initialized:
            await self.initialize()

        try:
            async with self.client.stream(
                "POST",
                "/api/generate",
                json={
                    "model": self.metadata.id,
                    "prompt": request.messages[-1]["content"] if request.messages else request.prompt,
                    "stream": True
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

        except Exception as e:
            logger.error(f"Error streaming with local model: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens (estimate)"""
        return len(text) // 4
