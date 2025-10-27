"""
YAGO Token Tracker - Real-time cost tracking
Tracks token usage and cost across all AI providers
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger("YAGO")


class TokenTracker:
    """Real-time token ve maliyet takip sistemi"""

    # API maliyet oranları (per 1M tokens)
    COST_PER_MILLION = {
        'anthropic': {
            'claude-3-5-sonnet-latest': {'input': 3.00, 'output': 15.00},
        },
        'openai': {
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
        },
        'google': {
            'gemini-2.0-flash-exp': {'input': 0.00, 'output': 0.00},  # Free tier
            'gemini-pro': {'input': 0.125, 'output': 0.375},
        }
    }

    def __init__(self):
        """Initialize tracker"""
        self.total_tokens = {
            'anthropic': {'input': 0, 'output': 0, 'total': 0},
            'openai': {'input': 0, 'output': 0, 'total': 0},
            'google': {'input': 0, 'output': 0, 'total': 0}
        }
        self.api_calls = {
            'anthropic': 0,
            'openai': 0,
            'google': 0
        }
        self.start_time = datetime.now()

    def track(self, provider: str, model: str, tokens: Dict[str, int]):
        """
        Token kullanımını kaydet

        Args:
            provider: 'anthropic', 'openai', 'google'
            model: Model adı
            tokens: {'input': X, 'output': Y, 'total': Z}
        """
        if provider not in self.total_tokens:
            logger.warning(f"Bilinmeyen provider: {provider}")
            return

        # Token sayılarını ekle
        input_tokens = tokens.get('input_tokens', tokens.get('prompt_tokens', 0))
        output_tokens = tokens.get('output_tokens', tokens.get('completion_tokens', 0))
        total_tokens = tokens.get('total_tokens', input_tokens + output_tokens)

        self.total_tokens[provider]['input'] += input_tokens
        self.total_tokens[provider]['output'] += output_tokens
        self.total_tokens[provider]['total'] += total_tokens
        self.api_calls[provider] += 1

        # Real-time log
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
        logger.info(
            f"{provider.upper()} | Model: {model} | "
            f"Tokens: {total_tokens:,} | Cost: ${cost:.4f}"
        )

    def _calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Maliyet hesapla

        Returns:
            Maliyet (USD)
        """
        if provider not in self.COST_PER_MILLION:
            return 0.0

        model_costs = self.COST_PER_MILLION[provider].get(model)
        if not model_costs:
            # Default to first model in provider
            model_costs = list(self.COST_PER_MILLION[provider].values())[0]

        input_cost = (input_tokens / 1_000_000) * model_costs['input']
        output_cost = (output_tokens / 1_000_000) * model_costs['output']

        return input_cost + output_cost

    def get_total_cost(self) -> Dict[str, float]:
        """
        Provider başına toplam maliyeti hesapla

        Returns:
            {'anthropic': X, 'openai': Y, 'google': Z, 'total': T}
        """
        costs = {}
        total_cost = 0.0

        for provider in self.total_tokens:
            provider_cost = 0.0

            # Her model için varsayılan fiyatı kullan
            if provider in self.COST_PER_MILLION:
                default_model = list(self.COST_PER_MILLION[provider].keys())[0]
                input_tokens = self.total_tokens[provider]['input']
                output_tokens = self.total_tokens[provider]['output']

                provider_cost = self._calculate_cost(
                    provider,
                    default_model,
                    input_tokens,
                    output_tokens
                )

            costs[provider] = provider_cost
            total_cost += provider_cost

        costs['total'] = total_cost
        return costs

    def get_stats(self) -> Dict:
        """
        Detaylı istatistikler

        Returns:
            Statistics dictionary
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        costs = self.get_total_cost()

        return {
            'duration_seconds': elapsed,
            'total_cost': costs['total'],
            'costs_by_provider': {k: v for k, v in costs.items() if k != 'total'},
            'tokens_by_provider': self.total_tokens,
            'api_calls': self.api_calls,
            'total_api_calls': sum(self.api_calls.values()),
            'total_tokens': sum(p['total'] for p in self.total_tokens.values())
        }

    def print_summary(self):
        """Özet rapor yazdır"""
        stats = self.get_stats()

        logger.info("=" * 60)
        logger.info("📊 TOKEN & COST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duration: {stats['duration_seconds']:.1f}s")
        logger.info(f"💰 Total Cost: ${stats['total_cost']:.4f}")
        logger.info(f"🔢 Total Tokens: {stats['total_tokens']:,}")
        logger.info(f"📞 Total API Calls: {stats['total_api_calls']}")
        logger.info("")
        logger.info("Provider Breakdown:")

        for provider in ['anthropic', 'openai', 'google']:
            tokens = stats['tokens_by_provider'][provider]
            calls = stats['api_calls'][provider]
            cost = stats['costs_by_provider'][provider]

            if calls > 0:
                logger.info(
                    f"  {provider.upper():12} | "
                    f"Calls: {calls:3} | "
                    f"Tokens: {tokens['total']:8,} | "
                    f"Cost: ${cost:.4f}"
                )

        logger.info("=" * 60)


# Global tracker instance
_tracker: Optional[TokenTracker] = None


def get_tracker() -> TokenTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = TokenTracker()
    return _tracker


def reset_tracker():
    """Reset global tracker"""
    global _tracker
    _tracker = TokenTracker()
