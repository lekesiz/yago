"""
Multi-AI Failover & Validation System
YAGO v5.5.0

Bir AI başarısız olursa, otomatik olarak diğer AI'lara geçiş yapar.
Her AI'ın cevabını diğer AI'larla doğrular.
En iyi sonucu seçer.
Offline AI modellerini destekler (Ollama, LM Studio).
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger("YAGO.AIFailover")


class AIProvider(Enum):
    """AI provider types"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"  # Offline models


class ResponseStatus(Enum):
    """Response status types"""
    SUCCESS = "success"
    EMPTY = "empty"
    ERROR = "error"
    TIMEOUT = "timeout"
    INVALID = "invalid"


@dataclass
class AIResponse:
    """AI response with metadata"""
    provider: AIProvider
    model: str
    content: str
    status: ResponseStatus
    error: Optional[str] = None
    tokens: int = 0
    duration: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ValidationResult:
    """Validation result from another AI"""
    validator_provider: AIProvider
    is_valid: bool
    confidence: float  # 0.0 - 1.0
    feedback: str
    issues: List[str]


class AIFailoverSystem:
    """
    Multi-AI failover and validation system

    Features:
    - Automatic failover to alternative AI providers
    - Cross-validation of responses
    - Quality scoring and best response selection
    - Retry with exponential backoff
    - Response caching for efficiency
    """

    def __init__(self, enable_offline: bool = True):
        """Initialize AI failover system

        Args:
            enable_offline: If True, detect and use offline AI models
        """
        self.providers = {
            AIProvider.ANTHROPIC: {
                "name": "Claude 3.5 Sonnet",
                "model": "claude-3-5-sonnet-latest",
                "priority": 1,  # Primary
                "strengths": ["planning", "analysis", "review"],
                "max_tokens": 200000,
                "timeout": 60
            },
            AIProvider.OPENAI: {
                "name": "GPT-4o",
                "model": "gpt-4o",
                "priority": 2,  # Secondary
                "strengths": ["coding", "documentation"],
                "max_tokens": 128000,
                "timeout": 60
            },
            AIProvider.GOOGLE: {
                "name": "Gemini 2.0 Flash",
                "model": "gemini-2.0-flash-exp",
                "priority": 3,  # Tertiary
                "strengths": ["testing", "validation"],
                "max_tokens": 1000000,
                "timeout": 45
            }
        }

        self.failure_history: List[Dict] = []
        self.validation_history: List[Dict] = []
        self.response_cache: Dict[str, AIResponse] = {}
        self.offline_models: List[Any] = []
        self.enable_offline = enable_offline

        # Initialize offline AI detection
        if enable_offline:
            self._detect_offline_models()

    def execute_with_failover(self,
                             task: str,
                             primary_provider: AIProvider,
                             llm_call_func: Callable,
                             max_retries: int = 3,
                             validate: bool = True,
                             **kwargs) -> AIResponse:
        """
        Execute task with automatic failover

        Args:
            task: Task description
            primary_provider: Primary AI provider to try first
            llm_call_func: Function to call LLM (takes provider, model, prompt)
            max_retries: Maximum retry attempts per provider
            validate: Whether to validate response with other AI
            **kwargs: Additional arguments for LLM call

        Returns:
            Best AIResponse from available providers
        """
        # Check cache first
        cache_key = self._get_cache_key(task, primary_provider)
        if cache_key in self.response_cache:
            logger.info(f"✅ Cache hit for task with {primary_provider.value}")
            return self.response_cache[cache_key]

        # Get provider order based on priority
        provider_order = self._get_provider_order(primary_provider)

        all_responses: List[AIResponse] = []

        # Try each provider in order
        for provider in provider_order:
            provider_config = self.providers[provider]
            logger.info(f"🔄 Trying {provider.value} ({provider_config['name']})")

            response = self._try_provider(
                provider=provider,
                task=task,
                llm_call_func=llm_call_func,
                max_retries=max_retries,
                **kwargs
            )

            if response.status == ResponseStatus.SUCCESS:
                all_responses.append(response)

                # If validation enabled, validate with other AI
                if validate and len(provider_order) > 1:
                    validation = self._validate_response(
                        response=response,
                        task=task,
                        validator_provider=self._get_next_provider(provider, provider_order),
                        llm_call_func=llm_call_func
                    )

                    if validation.is_valid and validation.confidence > 0.7:
                        logger.info(f"✅ Response validated by {validation.validator_provider.value}")
                        self.response_cache[cache_key] = response
                        return response
                    else:
                        logger.warning(f"⚠️ Response validation failed: {validation.feedback}")
                        # Continue to next provider
                else:
                    # No validation needed
                    self.response_cache[cache_key] = response
                    return response

            else:
                # Record failure
                self.failure_history.append({
                    "provider": provider.value,
                    "task": task[:100],
                    "status": response.status.value,
                    "error": response.error,
                    "timestamp": datetime.now()
                })
                logger.warning(f"❌ {provider.value} failed: {response.status.value}")

        # If we have any responses, return the best one
        if all_responses:
            best_response = self._select_best_response(all_responses, task)
            logger.info(f"✅ Selected best response from {best_response.provider.value}")
            self.response_cache[cache_key] = best_response
            return best_response

        # All providers failed
        error_response = AIResponse(
            provider=primary_provider,
            model="none",
            content="",
            status=ResponseStatus.ERROR,
            error="All AI providers failed to generate response"
        )
        logger.error("❌ All AI providers failed!")
        return error_response

    def _try_provider(self,
                     provider: AIProvider,
                     task: str,
                     llm_call_func: Callable,
                     max_retries: int = 3,
                     **kwargs) -> AIResponse:
        """Try a specific provider with retries"""
        provider_config = self.providers[provider]

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                # Call LLM
                result = llm_call_func(
                    provider=provider.value,
                    model=provider_config["model"],
                    prompt=task,
                    timeout=provider_config["timeout"],
                    **kwargs
                )

                duration = time.time() - start_time

                # Check response
                if result is None or result == "":
                    status = ResponseStatus.EMPTY
                    content = ""
                    error = "Empty response from LLM"
                elif isinstance(result, dict) and "error" in result:
                    status = ResponseStatus.ERROR
                    content = ""
                    error = result["error"]
                else:
                    status = ResponseStatus.SUCCESS
                    content = str(result)
                    error = None

                response = AIResponse(
                    provider=provider,
                    model=provider_config["model"],
                    content=content,
                    status=status,
                    error=error,
                    duration=duration
                )

                if status == ResponseStatus.SUCCESS:
                    logger.info(f"✅ {provider.value} succeeded in {duration:.2f}s")
                    return response
                else:
                    logger.warning(f"⚠️ {provider.value} attempt {attempt + 1}/{max_retries}: {error}")

                    # Exponential backoff
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"⏱️ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)

            except TimeoutError:
                logger.warning(f"⏱️ {provider.value} timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"❌ {provider.value} error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        # All retries failed
        return AIResponse(
            provider=provider,
            model=provider_config["model"],
            content="",
            status=ResponseStatus.ERROR,
            error=f"Failed after {max_retries} retries"
        )

    def _validate_response(self,
                          response: AIResponse,
                          task: str,
                          validator_provider: AIProvider,
                          llm_call_func: Callable) -> ValidationResult:
        """Validate response using another AI"""
        validator_config = self.providers[validator_provider]

        validation_prompt = f"""
Task: {task}

Response from {response.provider.value}:
{response.content}

Please validate this response:
1. Does it correctly address the task?
2. Is the quality acceptable?
3. Are there any issues or errors?

Respond in JSON format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "feedback": "Brief feedback",
    "issues": ["issue1", "issue2"]
}}
"""

        try:
            result = llm_call_func(
                provider=validator_provider.value,
                model=validator_config["model"],
                prompt=validation_prompt,
                timeout=30
            )

            # Parse validation result
            # (Simplified - in production, parse JSON properly)
            is_valid = "true" in str(result).lower()
            confidence = 0.8 if is_valid else 0.3

            validation = ValidationResult(
                validator_provider=validator_provider,
                is_valid=is_valid,
                confidence=confidence,
                feedback=str(result)[:200],
                issues=[]
            )

            self.validation_history.append({
                "original_provider": response.provider.value,
                "validator": validator_provider.value,
                "is_valid": is_valid,
                "confidence": confidence,
                "timestamp": datetime.now()
            })

            return validation

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return ValidationResult(
                validator_provider=validator_provider,
                is_valid=False,
                confidence=0.0,
                feedback=f"Validation error: {e}",
                issues=[str(e)]
            )

    def _select_best_response(self, responses: List[AIResponse], task: str) -> AIResponse:
        """Select best response from multiple responses"""
        # Score each response
        scored_responses = []

        for response in responses:
            score = 0.0

            # Length score (longer is usually better, up to a point)
            length = len(response.content)
            if 100 <= length <= 10000:
                score += 0.3
            elif length > 10000:
                score += 0.2

            # Speed score (faster is better)
            if response.duration < 10:
                score += 0.2
            elif response.duration < 30:
                score += 0.1

            # Provider priority score
            provider_config = self.providers[response.provider]
            if provider_config["priority"] == 1:
                score += 0.3
            elif provider_config["priority"] == 2:
                score += 0.2
            else:
                score += 0.1

            # Task-specific strengths
            task_lower = task.lower()
            strengths = provider_config.get("strengths", [])
            if any(strength in task_lower for strength in strengths):
                score += 0.2

            scored_responses.append((score, response))

        # Sort by score (descending)
        scored_responses.sort(key=lambda x: x[0], reverse=True)

        best_response = scored_responses[0][1]
        logger.info(f"🏆 Best response: {best_response.provider.value} (score: {scored_responses[0][0]:.2f})")

        return best_response

    def _get_provider_order(self, primary_provider: AIProvider) -> List[AIProvider]:
        """Get provider order based on priority"""
        # Primary first, then others by priority
        other_providers = [p for p in AIProvider if p != primary_provider]
        other_providers.sort(key=lambda p: self.providers[p]["priority"])

        return [primary_provider] + other_providers

    def _get_next_provider(self, current: AIProvider, provider_list: List[AIProvider]) -> AIProvider:
        """Get next provider from list"""
        current_idx = provider_list.index(current)
        next_idx = (current_idx + 1) % len(provider_list)
        return provider_list[next_idx]

    def _get_cache_key(self, task: str, provider: AIProvider) -> str:
        """Generate cache key"""
        import hashlib
        task_hash = hashlib.sha256(task.encode()).hexdigest()[:16]
        return f"{provider.value}:{task_hash}"

    def get_failure_stats(self) -> Dict[str, Any]:
        """Get failure statistics"""
        if not self.failure_history:
            return {"total_failures": 0}

        stats = {
            "total_failures": len(self.failure_history),
            "by_provider": {},
            "by_status": {}
        }

        for failure in self.failure_history:
            provider = failure["provider"]
            status = failure["status"]

            stats["by_provider"][provider] = stats["by_provider"].get(provider, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        return stats

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        if not self.validation_history:
            return {"total_validations": 0}

        stats = {
            "total_validations": len(self.validation_history),
            "success_rate": 0.0,
            "average_confidence": 0.0
        }

        valid_count = sum(1 for v in self.validation_history if v["is_valid"])
        stats["success_rate"] = valid_count / len(self.validation_history)

        avg_confidence = sum(v["confidence"] for v in self.validation_history) / len(self.validation_history)
        stats["average_confidence"] = avg_confidence

        return stats

    def _detect_offline_models(self):
        """Detect and register offline AI models"""
        try:
            from utils.offline_ai_detector import get_offline_ai_detector

            detector = get_offline_ai_detector()
            models = detector.detect_all_models()

            if models:
                logger.info(f"✅ Found {len(models)} offline AI models")

                # Add best offline model to providers with lowest priority
                for model in models:
                    # Create provider config for offline model
                    provider_key = AIProvider.OLLAMA

                    if provider_key not in self.providers:
                        self.providers[provider_key] = {
                            "name": f"Ollama: {model.name}",
                            "model": model.name,
                            "priority": 4,  # Lower priority than cloud models
                            "strengths": model.strengths,
                            "max_tokens": 4096,
                            "timeout": 120,
                            "offline": True,
                            "base_url": "http://localhost:11434"
                        }
                        logger.info(f"  ✅ Registered offline model: {model.name}")
                        break  # Just use the best one

                self.offline_models = models
            else:
                logger.info("ℹ️ No offline AI models found")

                # Try to download if none available
                detector.ensure_offline_model_available()

        except ImportError:
            logger.warning("⚠️ Offline AI detector not available")
        except Exception as e:
            logger.error(f"❌ Error detecting offline models: {e}")

    def get_offline_stats(self) -> Dict[str, Any]:
        """Get offline AI statistics"""
        if not self.offline_models:
            return {"offline_models": 0, "enabled": self.enable_offline}

        return {
            "offline_models": len(self.offline_models),
            "enabled": self.enable_offline,
            "models": [
                {
                    "name": m.name,
                    "provider": m.provider.value,
                    "size_gb": m.size_gb,
                    "parameters": m.parameters
                }
                for m in self.offline_models
            ]
        }


# Singleton instance
_ai_failover_instance = None


def get_ai_failover() -> AIFailoverSystem:
    """Get AIFailoverSystem singleton"""
    global _ai_failover_instance
    if _ai_failover_instance is None:
        _ai_failover_instance = AIFailoverSystem()
    return _ai_failover_instance


def reset_ai_failover():
    """Reset singleton (for testing)"""
    global _ai_failover_instance
    _ai_failover_instance = None


if __name__ == "__main__":
    # Test AI failover system
    failover = get_ai_failover()

    # Mock LLM call function
    def mock_llm_call(provider, model, prompt, timeout=60, **kwargs):
        print(f"Mock LLM call: {provider} - {model}")
        if provider == "anthropic":
            return "This is Claude's response"
        elif provider == "openai":
            return "This is GPT-4's response"
        else:
            return None

    # Test failover
    response = failover.execute_with_failover(
        task="Write a hello world program",
        primary_provider=AIProvider.ANTHROPIC,
        llm_call_func=mock_llm_call,
        validate=True
    )

    print(f"\nFinal response:")
    print(f"Provider: {response.provider.value}")
    print(f"Status: {response.status.value}")
    print(f"Content: {response.content}")

    print(f"\nStats:")
    print(f"Failures: {failover.get_failure_stats()}")
    print(f"Validations: {failover.get_validation_stats()}")
