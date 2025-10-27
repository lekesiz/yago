"""
Response Cache System
YAGO v5.8.0

SHA256-based caching for AI responses to reduce costs and improve speed.
- In-memory and disk-based caching
- TTL (time-to-live) support
- Cache statistics and hit rate tracking
- Automatic cache cleanup
- Cost savings calculation
"""

import hashlib
import json
import logging
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict

logger = logging.getLogger("YAGO.ResponseCache")


@dataclass
class CachedResponse:
    """Cached AI response with metadata"""
    key: str
    response: str
    provider: str
    model: str
    tokens: int
    cost: float
    timestamp: datetime
    ttl: int  # seconds
    hits: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl <= 0:  # -1 means never expire
            return False
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "key": self.key,
            "response": self.response,
            "provider": self.provider,
            "model": self.model,
            "tokens": self.tokens,
            "cost": self.cost,
            "timestamp": self.timestamp.isoformat(),
            "ttl": self.ttl,
            "hits": self.hits,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CachedResponse":
        """Create from dictionary"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class ResponseCache:
    """
    Response Cache System

    Features:
    - SHA256-based key generation from prompts
    - In-memory LRU cache with configurable size
    - Disk persistence for long-term caching
    - TTL support for automatic expiration
    - Cache statistics (hit rate, savings)
    - Automatic cleanup of expired entries
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,  # 1 hour
        cache_dir: Optional[Path] = None,
        enable_disk_cache: bool = True
    ):
        """
        Initialize response cache

        Args:
            max_size: Maximum number of entries in memory
            default_ttl: Default TTL in seconds (-1 for never expire)
            cache_dir: Directory for disk cache
            enable_disk_cache: Enable persistent disk caching
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_disk_cache = enable_disk_cache

        # In-memory cache (LRU)
        self.cache: OrderedDict[str, CachedResponse] = OrderedDict()

        # Statistics
        self.hits = 0
        self.misses = 0
        self.total_tokens_saved = 0
        self.total_cost_saved = 0.0

        # Disk cache directory
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "cache" / "responses"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load from disk if enabled
        if self.enable_disk_cache:
            self._load_from_disk()

    def _generate_key(self, prompt: str, provider: str, model: str, **kwargs) -> str:
        """
        Generate SHA256 hash key from prompt and metadata

        Args:
            prompt: The input prompt
            provider: AI provider name
            model: Model name
            **kwargs: Additional parameters that affect the response

        Returns:
            SHA256 hash string
        """
        # Combine prompt with relevant parameters
        key_data = {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        # Create deterministic string
        key_string = json.dumps(key_data, sort_keys=True)

        # Generate SHA256 hash
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, prompt: str, provider: str, model: str, **kwargs) -> Optional[str]:
        """
        Get cached response if available

        Args:
            prompt: The input prompt
            provider: AI provider name
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Cached response string or None if not found/expired
        """
        key = self._generate_key(prompt, provider, model, **kwargs)

        # Check in-memory cache first
        if key in self.cache:
            entry = self.cache[key]

            # Check if expired
            if entry.is_expired():
                logger.debug(f"Cache entry expired: {key[:16]}...")
                self._remove(key)
                self.misses += 1
                return None

            # Cache hit!
            self.hits += 1
            entry.hits += 1

            # Move to end (LRU)
            self.cache.move_to_end(key)

            # Update statistics
            self.total_tokens_saved += entry.tokens
            self.total_cost_saved += entry.cost

            logger.info(f"✅ Cache HIT: {key[:16]}... (saved {entry.tokens} tokens, ${entry.cost:.4f})")
            return entry.response

        # Cache miss
        self.misses += 1
        logger.debug(f"Cache MISS: {key[:16]}...")
        return None

    def set(
        self,
        prompt: str,
        response: str,
        provider: str,
        model: str,
        tokens: int = 0,
        cost: float = 0.0,
        ttl: Optional[int] = None,
        **kwargs
    ):
        """
        Store response in cache

        Args:
            prompt: The input prompt
            response: The AI response
            provider: AI provider name
            model: Model name
            tokens: Token count
            cost: Cost in USD
            ttl: Time-to-live in seconds (None = use default)
            **kwargs: Additional parameters
        """
        key = self._generate_key(prompt, provider, model, **kwargs)
        ttl = ttl if ttl is not None else self.default_ttl

        # Create cache entry
        entry = CachedResponse(
            key=key,
            response=response,
            provider=provider,
            model=model,
            tokens=tokens,
            cost=cost,
            timestamp=datetime.now(),
            ttl=ttl,
        )

        # Add to in-memory cache
        self.cache[key] = entry

        # Move to end (most recent)
        self.cache.move_to_end(key)

        # Enforce max size (LRU eviction)
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            logger.debug(f"Cache full, evicting: {oldest_key[:16]}...")
            self._remove(oldest_key)

        # Save to disk if enabled
        if self.enable_disk_cache:
            self._save_to_disk(key, entry)

        logger.debug(f"Cached response: {key[:16]}... (ttl={ttl}s)")

    def _remove(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]

        # Remove from disk
        if self.enable_disk_cache:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()

    def _save_to_disk(self, key: str, entry: CachedResponse):
        """Save cache entry to disk"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                json.dump(entry.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache to disk: {e}")

    def _load_from_disk(self):
        """Load cache entries from disk"""
        if not self.cache_dir.exists():
            return

        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        entry = CachedResponse.from_dict(data)

                        # Skip expired entries
                        if entry.is_expired():
                            cache_file.unlink()
                            continue

                        # Add to in-memory cache
                        self.cache[entry.key] = entry

                except Exception as e:
                    logger.error(f"Failed to load cache file {cache_file}: {e}")
                    continue

            logger.info(f"📂 Loaded {len(self.cache)} cache entries from disk")

        except Exception as e:
            logger.error(f"Failed to load cache from disk: {e}")

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()

        # Clear disk cache
        if self.enable_disk_cache:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()

        logger.info("🗑️ Cache cleared")

    def cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

        for key in expired_keys:
            self._remove(key)

        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0

        return {
            "total_entries": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "tokens_saved": self.total_tokens_saved,
            "cost_saved": round(self.total_cost_saved, 4),
            "disk_cache_enabled": self.enable_disk_cache,
        }

    def get_top_entries(self, n: int = 10) -> list[CachedResponse]:
        """Get top N most frequently used cache entries"""
        sorted_entries = sorted(self.cache.values(), key=lambda e: e.hits, reverse=True)
        return sorted_entries[:n]

    def export_stats_report(self, output_file: Optional[Path] = None) -> str:
        """Generate cache statistics report"""
        stats = self.get_stats()

        report = []
        report.append("=" * 80)
        report.append("💾 YAGO RESPONSE CACHE STATISTICS")
        report.append("=" * 80)
        report.append(f"\n📊 CACHE METRICS")
        report.append("-" * 80)
        report.append(f"Total Entries: {stats['total_entries']}/{stats['max_size']}")
        report.append(f"Total Requests: {stats['total_requests']}")
        report.append(f"Cache Hits: {stats['hits']}")
        report.append(f"Cache Misses: {stats['misses']}")
        report.append(f"Hit Rate: {stats['hit_rate']}%")

        report.append(f"\n💰 COST SAVINGS")
        report.append("-" * 80)
        report.append(f"Tokens Saved: {stats['tokens_saved']:,}")
        report.append(f"Cost Saved: ${stats['cost_saved']:.4f}")

        report.append(f"\n🏆 TOP CACHED QUERIES")
        report.append("-" * 80)
        top_entries = self.get_top_entries(5)
        for i, entry in enumerate(top_entries, 1):
            age = (datetime.now() - entry.timestamp).total_seconds() / 60
            report.append(f"{i}. {entry.provider}/{entry.model}")
            report.append(f"   Hits: {entry.hits}, Age: {age:.1f}min, Tokens: {entry.tokens}")

        report.append("\n" + "=" * 80)

        report_text = "\n".join(report)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"📄 Cache report saved to: {output_file}")

        return report_text


# Singleton instance
_response_cache_instance = None


def get_response_cache() -> ResponseCache:
    """Get ResponseCache singleton"""
    global _response_cache_instance
    if _response_cache_instance is None:
        _response_cache_instance = ResponseCache()
    return _response_cache_instance


def reset_response_cache():
    """Reset singleton (for testing)"""
    global _response_cache_instance
    _response_cache_instance = None


if __name__ == "__main__":
    # Test response cache
    cache = get_response_cache()

    # Test cache miss
    result = cache.get("Write a hello world program", "anthropic", "claude-3-5-sonnet")
    print(f"Cache miss: {result is None}")  # Should be True

    # Store response
    cache.set(
        prompt="Write a hello world program",
        response="print('Hello, World!')",
        provider="anthropic",
        model="claude-3-5-sonnet",
        tokens=100,
        cost=0.001
    )

    # Test cache hit
    result = cache.get("Write a hello world program", "anthropic", "claude-3-5-sonnet")
    print(f"Cache hit: {result is not None}")  # Should be True
    print(f"Response: {result}")

    # Get statistics
    print("\n" + cache.export_stats_report())

    # Cleanup
    cache.cleanup_expired()
