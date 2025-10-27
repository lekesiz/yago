"""
Smart Caching System for YAGO
Caches AI responses to reduce API calls and costs
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("YAGO")


class SmartCache:
    """Smart caching for AI responses"""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.hits = 0
        self.misses = 0

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model"""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{key}.cache"

    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response"""
        key = self._get_cache_key(prompt, model)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            self.misses += 1
            return None

        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)

            # Check TTL
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for {key[:8]}")
                cache_path.unlink()
                self.misses += 1
                return None

            self.hits += 1
            logger.info(f"💾 Cache HIT for {model} ({key[:8]})")
            return data['response']

        except Exception as e:
            logger.error(f"Cache read error: {e}")
            self.misses += 1
            return None

    def set(self, prompt: str, model: str, response: str):
        """Cache response"""
        key = self._get_cache_key(prompt, model)
        cache_path = self._get_cache_path(key)

        data = {
            'prompt': prompt,
            'model': model,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"💾 Cached response for {model} ({key[:8]})")
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def clear(self):
        """Clear all cache"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        logger.info("🗑️  Cache cleared")
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 1),
            'cached_items': len(cache_files),
            'cache_size_mb': round(total_size / 1024 / 1024, 2)
        }


_smart_cache: Optional[SmartCache] = None


def get_smart_cache(cache_dir: str = ".cache", ttl_hours: int = 24) -> SmartCache:
    """Get smart cache singleton"""
    global _smart_cache
    if _smart_cache is None:
        _smart_cache = SmartCache(cache_dir, ttl_hours)
    return _smart_cache


def reset_smart_cache():
    """Reset cache"""
    global _smart_cache
    _smart_cache = None
