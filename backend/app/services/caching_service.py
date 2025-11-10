"""
Caching service for frequently assessed locations.

Implements Redis-based caching with TTL for risk assessments.
"""
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import timedelta
import asyncio

from app.models import HazardType


class CacheKey:
    """Helper for generating consistent cache keys."""
    
    @staticmethod
    def risk_assessment(
        latitude: float,
        longitude: float,
        hazard_types: list[HazardType],
        risk_factors: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Generate cache key for risk assessment.
        
        Args:
            latitude: Location latitude (rounded to 4 decimals ~11m precision)
            longitude: Location longitude
            hazard_types: List of hazard types being assessed
            risk_factors: Optional custom risk factors
            
        Returns:
            Cache key string
        """
        # Round coordinates to reduce cache fragmentation
        # 4 decimal places = ~11m precision, good balance
        lat_rounded = round(latitude, 4)
        lon_rounded = round(longitude, 4)
        
        # Sort hazard types for consistency
        hazards_str = ",".join(sorted(h.value if hasattr(h, 'value') else str(h) for h in hazard_types))
        
        # Include risk factors if provided
        factors_str = ""
        if risk_factors:
            # Sort keys for consistency
            sorted_factors = sorted(risk_factors.items())
            factors_str = json.dumps(sorted_factors)
        
        # Generate key
        key_parts = [
            f"risk_assessment",
            f"lat:{lat_rounded}",
            f"lon:{lon_rounded}",
            f"hazards:{hazards_str}",
            f"factors:{factors_str}" if factors_str else ""
        ]
        
        key = ":".join(part for part in key_parts if part)
        return key
    
    @staticmethod
    def location_by_coords(latitude: float, longitude: float) -> str:
        """Generate cache key for location lookup by coordinates."""
        lat_rounded = round(latitude, 4)
        lon_rounded = round(longitude, 4)
        return f"location:coords:{lat_rounded}:{lon_rounded}"


class InMemoryCache:
    """
    Simple in-memory LRU cache for risk assessments.
    
    For production, replace with Redis or Memcached.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            default_ttl_seconds: Default TTL for cached items (1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: list[str] = []  # LRU tracking
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            if key not in self._cache:
                return None
            
            cached_item = self._cache[key]
            
            # Check if expired
            import time
            if time.time() > cached_item['expires_at']:
                # Remove expired item
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return None
            
            # Update access order (move to end)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return cached_item['value']
    
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl_seconds: TTL in seconds (uses default if None)
        """
        async with self._lock:
            import time
            
            ttl = ttl_seconds or self.default_ttl
            expires_at = time.time() + ttl
            
            # If cache is full, remove least recently used
            if len(self._cache) >= self.max_size and key not in self._cache:
                if self._access_order:
                    lru_key = self._access_order.pop(0)
                    del self._cache[lru_key]
            
            # Store item
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            
            # Update access order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
    
    async def delete(self, key: str) -> None:
        """Delete item from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
    
    async def clear(self) -> None:
        """Clear all cached items."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        async with self._lock:
            import time
            
            # Count expired items
            expired_count = sum(
                1 for item in self._cache.values()
                if time.time() > item['expires_at']
            )
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'utilization': len(self._cache) / self.max_size,
                'expired_count': expired_count,
                'default_ttl_seconds': self.default_ttl
            }


class CachingService:
    """
    Service for caching risk assessments with invalidation strategy.
    """
    
    def __init__(self, cache: Optional[InMemoryCache] = None):
        """
        Initialize caching service.
        
        Args:
            cache: Cache implementation (creates default if None)
        """
        self.cache = cache or InMemoryCache()
        self.hit_count = 0
        self.miss_count = 0
    
    async def get_risk_assessment(
        self,
        latitude: float,
        longitude: float,
        hazard_types: list[HazardType],
        risk_factors: Optional[Dict[str, float]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached risk assessment.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            hazard_types: Hazard types to assess
            risk_factors: Optional custom risk factors
            
        Returns:
            Cached assessment or None
        """
        key = CacheKey.risk_assessment(latitude, longitude, hazard_types, risk_factors)
        result = await self.cache.get(key)
        
        if result:
            self.hit_count += 1
        else:
            self.miss_count += 1
        
        return result
    
    async def set_risk_assessment(
        self,
        latitude: float,
        longitude: float,
        hazard_types: list[HazardType],
        assessment_result: Dict[str, Any],
        risk_factors: Optional[Dict[str, float]] = None,
        ttl_seconds: int = 3600
    ) -> None:
        """
        Cache risk assessment result.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            hazard_types: Hazard types assessed
            assessment_result: Assessment result to cache
            risk_factors: Optional custom risk factors
            ttl_seconds: Cache TTL (default 1 hour)
        """
        key = CacheKey.risk_assessment(latitude, longitude, hazard_types, risk_factors)
        await self.cache.set(key, assessment_result, ttl_seconds)
    
    async def invalidate_location(self, latitude: float, longitude: float) -> None:
        """
        Invalidate all cached assessments for a location.
        
        Called when location data is updated.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
        """
        # In production with Redis, use key pattern matching
        # For now, just note that this location's cache should be invalidated
        # The TTL will handle cleanup
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get caching statistics.
        
        Returns:
            Dictionary with hit rate, miss rate, etc.
        """
        cache_stats = await self.cache.get_stats()
        
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            **cache_stats,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate * 100, 2)
        }
    
    async def clear_stats(self) -> None:
        """Reset hit/miss counters."""
        self.hit_count = 0
        self.miss_count = 0


# Global cache instance
_cache_service: Optional[CachingService] = None


def get_cache_service() -> CachingService:
    """
    Get global cache service instance.
    
    Returns:
        CachingService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CachingService()
    return _cache_service
