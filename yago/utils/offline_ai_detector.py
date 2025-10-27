"""
Offline AI Model Detection and Management
YAGO v5.5.0

Detects local offline AI models (Ollama, LM Studio, etc.)
Downloads suitable models if none exist
Integrates with AI failover system
"""

import subprocess
import logging
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger("YAGO.OfflineAI")


class OfflineProvider(Enum):
    """Offline AI provider types"""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    LLAMACPP = "llamacpp"


@dataclass
class OfflineModel:
    """Offline AI model information"""
    provider: OfflineProvider
    name: str
    size_gb: float
    parameters: str  # e.g., "7B", "13B"
    quantization: Optional[str] = None  # e.g., "Q4_K_M"
    available: bool = False
    download_url: Optional[str] = None
    strengths: List[str] = None

    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []


class OfflineAIDetector:
    """
    Offline AI Model Detection and Management

    Features:
    - Detect Ollama models on local machine
    - Detect LM Studio models
    - Download suitable models if none exist
    - Integrate with AI failover system
    - Prioritize models based on task requirements
    """

    def __init__(self):
        """Initialize offline AI detector"""
        self.detected_models: List[OfflineModel] = []
        self.ollama_available = False
        self.lm_studio_available = False

        # Recommended models (smallest to largest)
        self.recommended_models = [
            {
                "name": "qwen2.5:3b",
                "provider": OfflineProvider.OLLAMA,
                "size_gb": 2.0,
                "parameters": "3B",
                "strengths": ["fast", "coding", "general"],
                "download_url": "ollama pull qwen2.5:3b"
            },
            {
                "name": "llama3.2:3b",
                "provider": OfflineProvider.OLLAMA,
                "size_gb": 2.0,
                "parameters": "3B",
                "strengths": ["fast", "general", "chat"],
                "download_url": "ollama pull llama3.2:3b"
            },
            {
                "name": "phi3:mini",
                "provider": OfflineProvider.OLLAMA,
                "size_gb": 2.3,
                "parameters": "3.8B",
                "strengths": ["fast", "coding", "reasoning"],
                "download_url": "ollama pull phi3:mini"
            },
            {
                "name": "mistral:7b",
                "provider": OfflineProvider.OLLAMA,
                "size_gb": 4.1,
                "parameters": "7B",
                "strengths": ["coding", "general", "reasoning"],
                "download_url": "ollama pull mistral:7b"
            },
            {
                "name": "codellama:7b",
                "provider": OfflineProvider.OLLAMA,
                "size_gb": 3.8,
                "parameters": "7B",
                "strengths": ["coding", "debugging", "refactoring"],
                "download_url": "ollama pull codellama:7b"
            },
        ]

    def detect_all_models(self) -> List[OfflineModel]:
        """
        Detect all available offline AI models

        Returns:
            List of detected OfflineModel instances
        """
        logger.info("🔍 Scanning for offline AI models...")

        self.detected_models = []

        # Detect Ollama
        ollama_models = self._detect_ollama()
        self.detected_models.extend(ollama_models)

        # Detect LM Studio
        lm_studio_models = self._detect_lm_studio()
        self.detected_models.extend(lm_studio_models)

        if self.detected_models:
            logger.info(f"✅ Found {len(self.detected_models)} offline models")
            for model in self.detected_models:
                logger.info(f"  - {model.name} ({model.parameters}, {model.size_gb}GB)")
        else:
            logger.warning("❌ No offline AI models found")

        return self.detected_models

    def _detect_ollama(self) -> List[OfflineModel]:
        """Detect Ollama models"""
        models = []

        try:
            # Check if Ollama is installed
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.ollama_available = True
                logger.info("✅ Ollama detected")

                # Parse Ollama list output
                lines = result.stdout.strip().split('\n')

                # Skip header line
                for line in lines[1:]:
                    if not line.strip():
                        continue

                    parts = line.split()
                    if len(parts) >= 3:
                        model_name = parts[0]
                        size_str = parts[2] if len(parts) > 2 else "0GB"

                        # Parse size (e.g., "4.1GB" -> 4.1)
                        size_gb = self._parse_size(size_str)

                        # Determine parameters from name or size
                        parameters = self._estimate_parameters(model_name, size_gb)

                        # Determine strengths from model name
                        strengths = self._determine_strengths(model_name)

                        model = OfflineModel(
                            provider=OfflineProvider.OLLAMA,
                            name=model_name,
                            size_gb=size_gb,
                            parameters=parameters,
                            available=True,
                            strengths=strengths
                        )
                        models.append(model)
            else:
                logger.info("❌ Ollama not found")

        except FileNotFoundError:
            logger.info("❌ Ollama not installed")
        except subprocess.TimeoutExpired:
            logger.warning("⏱️ Ollama command timeout")
        except Exception as e:
            logger.error(f"❌ Error detecting Ollama: {e}")

        return models

    def _detect_lm_studio(self) -> List[OfflineModel]:
        """Detect LM Studio models"""
        models = []

        # LM Studio typically stores models in:
        # macOS: ~/Library/Application Support/LM Studio/models
        # Windows: %USERPROFILE%\.cache\lm-studio\models
        # Linux: ~/.cache/lm-studio/models

        possible_paths = [
            Path.home() / "Library" / "Application Support" / "LM Studio" / "models",
            Path.home() / ".cache" / "lm-studio" / "models",
            Path.home() / ".cache" / "lmstudio" / "models",
        ]

        for models_dir in possible_paths:
            if models_dir.exists():
                self.lm_studio_available = True
                logger.info(f"✅ LM Studio models directory found: {models_dir}")

                # Scan for .gguf files
                gguf_files = list(models_dir.rglob("*.gguf"))

                for gguf_file in gguf_files:
                    size_gb = gguf_file.stat().st_size / (1024**3)
                    model_name = gguf_file.stem

                    parameters = self._estimate_parameters(model_name, size_gb)
                    strengths = self._determine_strengths(model_name)

                    model = OfflineModel(
                        provider=OfflineProvider.LM_STUDIO,
                        name=model_name,
                        size_gb=size_gb,
                        parameters=parameters,
                        available=True,
                        strengths=strengths
                    )
                    models.append(model)

                break

        if not self.lm_studio_available:
            logger.info("❌ LM Studio not found")

        return models

    def _parse_size(self, size_str: str) -> float:
        """Parse size string to GB"""
        try:
            # Remove "GB" and convert to float
            size_str = size_str.upper().replace("GB", "").replace("MB", "").strip()
            size = float(size_str)

            # If was MB, convert to GB
            if "MB" in size_str.upper():
                size = size / 1024

            return size
        except:
            return 0.0

    def _estimate_parameters(self, model_name: str, size_gb: float) -> str:
        """Estimate parameter count from model name or size"""
        model_lower = model_name.lower()

        # Check name first
        if "3b" in model_lower or "3.8b" in model_lower:
            return "3B"
        elif "7b" in model_lower:
            return "7B"
        elif "13b" in model_lower:
            return "13B"
        elif "33b" in model_lower or "34b" in model_lower:
            return "33B"
        elif "70b" in model_lower:
            return "70B"

        # Estimate from size (rough estimates for Q4 quantization)
        if size_gb < 3:
            return "3B"
        elif size_gb < 6:
            return "7B"
        elif size_gb < 10:
            return "13B"
        elif size_gb < 25:
            return "33B"
        else:
            return "70B"

    def _determine_strengths(self, model_name: str) -> List[str]:
        """Determine model strengths from name"""
        model_lower = model_name.lower()
        strengths = []

        if "code" in model_lower or "coder" in model_lower:
            strengths.extend(["coding", "debugging", "refactoring"])
        elif "mistral" in model_lower or "mixtral" in model_lower:
            strengths.extend(["coding", "general", "reasoning"])
        elif "llama" in model_lower:
            strengths.extend(["general", "chat", "reasoning"])
        elif "phi" in model_lower:
            strengths.extend(["coding", "reasoning", "fast"])
        elif "qwen" in model_lower:
            strengths.extend(["coding", "general", "multilingual"])
        elif "gemma" in model_lower:
            strengths.extend(["general", "chat", "safe"])
        else:
            strengths.append("general")

        # Size-based strengths
        if "3b" in model_lower or "mini" in model_lower:
            strengths.append("fast")

        return strengths

    def get_best_model_for_task(self, task: str) -> Optional[OfflineModel]:
        """
        Get best offline model for a specific task

        Args:
            task: Task description

        Returns:
            Best matching OfflineModel or None
        """
        if not self.detected_models:
            logger.warning("No offline models available")
            return None

        task_lower = task.lower()

        # Score each model
        scored_models = []

        for model in self.detected_models:
            score = 0.0

            # Task-specific scoring
            if any(keyword in task_lower for keyword in ["code", "coding", "programming", "debug"]):
                if "coding" in model.strengths or "debugging" in model.strengths:
                    score += 0.4

            if any(keyword in task_lower for keyword in ["plan", "design", "architect"]):
                if "reasoning" in model.strengths:
                    score += 0.3

            if any(keyword in task_lower for keyword in ["test", "testing", "qa"]):
                if "general" in model.strengths:
                    score += 0.2

            # Speed bonus for smaller models
            if "fast" in model.strengths:
                score += 0.2

            # Size penalty for very large models (slower)
            if model.size_gb > 10:
                score -= 0.1

            scored_models.append((score, model))

        # Sort by score
        scored_models.sort(key=lambda x: x[0], reverse=True)

        best_model = scored_models[0][1]
        logger.info(f"🏆 Best offline model for task: {best_model.name} (score: {scored_models[0][0]:.2f})")

        return best_model

    def download_recommended_model(self, prefer_coding: bool = True) -> Optional[OfflineModel]:
        """
        Download smallest recommended model if no models exist

        Args:
            prefer_coding: If True, prefer coding-focused models

        Returns:
            Downloaded OfflineModel or None
        """
        if not self.ollama_available:
            logger.error("❌ Ollama not installed. Cannot download models.")
            logger.info("💡 Install Ollama: https://ollama.ai/download")
            return None

        # Find smallest suitable model
        candidates = self.recommended_models.copy()

        if prefer_coding:
            # Prioritize coding models
            candidates.sort(key=lambda x: (
                0 if "coding" in x["strengths"] else 1,
                x["size_gb"]
            ))
        else:
            # Just sort by size
            candidates.sort(key=lambda x: x["size_gb"])

        best_candidate = candidates[0]

        logger.info(f"📥 Downloading recommended model: {best_candidate['name']} ({best_candidate['size_gb']}GB)")

        try:
            # Download using Ollama
            result = subprocess.run(
                best_candidate["download_url"].split(),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            if result.returncode == 0:
                logger.info(f"✅ Successfully downloaded {best_candidate['name']}")

                # Create OfflineModel instance
                model = OfflineModel(
                    provider=best_candidate["provider"],
                    name=best_candidate["name"],
                    size_gb=best_candidate["size_gb"],
                    parameters=best_candidate["parameters"],
                    available=True,
                    strengths=best_candidate["strengths"]
                )

                # Add to detected models
                self.detected_models.append(model)

                return model
            else:
                logger.error(f"❌ Download failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("⏱️ Download timeout (10 minutes)")
            return None
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return None

    def ensure_offline_model_available(self, task: str = "") -> Optional[OfflineModel]:
        """
        Ensure at least one offline model is available

        Args:
            task: Task description for model selection

        Returns:
            Available OfflineModel or None
        """
        # First, detect existing models
        self.detect_all_models()

        if self.detected_models:
            # Found models, return best one for task
            if task:
                return self.get_best_model_for_task(task)
            else:
                return self.detected_models[0]

        # No models found, try to download
        logger.warning("⚠️ No offline models found. Attempting to download...")

        prefer_coding = "code" in task.lower() or "programming" in task.lower()
        return self.download_recommended_model(prefer_coding=prefer_coding)

    def get_ollama_api_config(self, model: OfflineModel) -> Dict[str, Any]:
        """
        Get Ollama API configuration for a model

        Args:
            model: OfflineModel to get config for

        Returns:
            API configuration dict
        """
        return {
            "provider": "ollama",
            "model": model.name,
            "base_url": "http://localhost:11434",
            "api_key": "ollama",  # Ollama doesn't need API key
            "timeout": 120,
            "max_tokens": 4096,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get offline AI statistics"""
        return {
            "total_models": len(self.detected_models),
            "ollama_available": self.ollama_available,
            "lm_studio_available": self.lm_studio_available,
            "models": [
                {
                    "name": m.name,
                    "provider": m.provider.value,
                    "size_gb": m.size_gb,
                    "parameters": m.parameters,
                    "strengths": m.strengths
                }
                for m in self.detected_models
            ]
        }


# Singleton instance
_offline_ai_instance = None


def get_offline_ai_detector() -> OfflineAIDetector:
    """Get OfflineAIDetector singleton"""
    global _offline_ai_instance
    if _offline_ai_instance is None:
        _offline_ai_instance = OfflineAIDetector()
    return _offline_ai_instance


def reset_offline_ai_detector():
    """Reset singleton (for testing)"""
    global _offline_ai_instance
    _offline_ai_instance = None


if __name__ == "__main__":
    # Test offline AI detector
    detector = get_offline_ai_detector()

    print("🔍 Detecting offline AI models...")
    models = detector.detect_all_models()

    print(f"\n📊 Found {len(models)} models:")
    for model in models:
        print(f"  - {model.name} ({model.provider.value})")
        print(f"    Parameters: {model.parameters}, Size: {model.size_gb}GB")
        print(f"    Strengths: {', '.join(model.strengths)}")

    if models:
        print("\n🎯 Testing best model selection:")
        test_tasks = [
            "Write Python code for a calculator",
            "Plan a web application architecture",
            "Create unit tests for a function"
        ]

        for task in test_tasks:
            best = detector.get_best_model_for_task(task)
            if best:
                print(f"  Task: {task}")
                print(f"  Best: {best.name}\n")
    else:
        print("\n⚠️ No models found. Would you like to download one?")
        print("Run: detector.download_recommended_model()")

    print(f"\n📈 Stats: {detector.get_stats()}")
