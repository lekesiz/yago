"""
YAGO Base Agent - Tüm ajanlar için temel sınıf
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from crewai import Agent, LLM
from dotenv import load_dotenv

# Import Token Tracker
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.token_tracker import get_tracker

# .env dosyasını yükle
load_dotenv()

logger = logging.getLogger("YAGO")


class BaseAgent:
    """Tüm YAGO ajanları için temel sınıf"""

    def __init__(self, config_path: str = "yago_config.yaml"):
        """
        Args:
            config_path: YAGO konfigürasyon dosyası yolu
        """
        self.config = self._load_config(config_path)
        self.llm_cache: Dict[str, Any] = {}

    def _load_config(self, config_path: str) -> Dict:
        """Konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Config yüklenemedi: {e}")

    def _get_llm(self, provider: str, model: str, temperature: float = 0.3):
        """
        Provider'a göre LLM instance döndür (CrewAI LLM format)

        Args:
            provider: "openai", "anthropic", veya "google"
            model: Model adı
            temperature: Temperature değeri

        Returns:
            CrewAI LLM instance
        """
        cache_key = f"{provider}:{model}:{temperature}"

        if cache_key in self.llm_cache:
            return self.llm_cache[cache_key]

        # CrewAI LLM kullan
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY bulunamadı!")

            llm = LLM(
                model=f"openai/{model}",
                temperature=temperature,
                api_key=api_key,
            )

        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY bulunamadı!")

            try:
                llm = LLM(
                    model=f"anthropic/{model}",
                    temperature=temperature,
                    api_key=api_key,
                )
            except TypeError as e:
                # Fallback: CrewAI/Anthropic SDK compatibility fix
                if "proxies" in str(e):
                    logger.warning(f"⚠️ Anthropic SDK compatibility issue detected, using alternative initialization")
                    # Use direct anthropic client initialization
                    import anthropic
                    from crewai import LLM as CrewLLM
                    llm = CrewLLM(
                        model=f"anthropic/{model}",
                        temperature=temperature,
                    )
                else:
                    raise

        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY bulunamadı!")

            llm = LLM(
                model=f"google/{model}",
                temperature=temperature,
                api_key=api_key,
            )

        else:
            raise ValueError(f"Bilinmeyen provider: {provider}")

        self.llm_cache[cache_key] = llm
        return llm

    def create_agent(
        self,
        agent_type: str,
        tools: Optional[list] = None,
        allow_delegation: bool = False,
    ) -> Agent:
        """
        Belirtilen tipte bir CrewAI ajanı oluştur

        Args:
            agent_type: "planner", "coder", "tester", vb.
            tools: Ajanın kullanacağı araçlar
            allow_delegation: Görev devri izni

        Returns:
            CrewAI Agent instance
        """
        # Config'den ajan bilgilerini al
        if agent_type == "orchestrator":
            agent_config = self.config.get("orchestrator", {})
        else:
            agent_config = self.config.get("agents", {}).get(agent_type, {})

        if not agent_config:
            raise ValueError(f"Agent config bulunamadı: {agent_type}")

        # LLM oluştur
        llm = self._get_llm(
            provider=agent_config["provider"],
            model=agent_config["model"],
            temperature=agent_config.get("temperature", 0.3),
        )

        # Max iterations ayarı
        max_iter = agent_config.get("max_iterations", 25)  # Default 25

        # CrewAI Agent oluştur
        agent = Agent(
            role=agent_config["role"],
            goal=agent_config["description"],
            backstory=f"Sen {agent_config['role']} rolündesin. {agent_config['description']}",
            verbose=True,
            llm=llm,
            tools=tools or [],
            allow_delegation=allow_delegation,
            max_iter=max_iter,  # Iteration limiti
        )

        return agent

    def get_workspace_path(self) -> Path:
        """Workspace dizinini döndür"""
        workspace = Path(self.config["sandbox"]["workspace_dir"]).resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
