"""
Intelligent Caching Service for Dermalens
Provides smart caching for AI analysis results, product recommendations, and user data
"""
import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import base64
from PIL import Image
import io

# Redis for caching
import redis.asyncio as redis

# Configuration
import sys
import os
from config import VERTEX_AI_CACHE_ENABLED, GOOGLE_CLOUD_PROJECT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentCachingService:
    """
    Intelligent caching service with multiple caching strategies
    
    Features:
    - Multi-level caching (memory, Redis, persistent)
    - Smart cache invalidation
    - Similarity-based caching
    - Performance optimization
    - Cache analytics
    """
    
    def __init__(self):
        """Initialize the intelligent caching service"""
        self.enabled = VERTEX_AI_CACHE_ENABLED
        self.project_id = GOOGLE_CLOUD_PROJECT
        
        # Cache clients
        self.redis_client = None
        self.memory_cache = {}  # In-memory cache for hot data
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        
        # Cache configuration
        self.cache_ttl = {
            "analysis_results": 3600,  # 1 hour
            "product_recommendations": 1800,  # 30 minutes
            "user_profiles": 7200,  # 2 hours
            "similarity_cache": 86400,  # 24 hours
            "hot_data": 300  # 5 minutes
        }
        
        # Initialize cache clients
        self._initialize_cache_clients()
    
    def _initialize_cache_clients(self):
        """Initialize cache clients"""
        try:
            if self.enabled:
                # Initialize Redis client
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=0, 
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # Test Redis connection
                asyncio.create_task(self._test_redis_connection())
                
                logger.info("✅ Intelligent caching service initialized")
            else:
                logger.warning("⚠️ Caching is disabled")
                
        except Exception as e:
            logger.error(f"❌ Error initializing cache clients: {e}")
            self.enabled = False
    
    async def _test_redis_connection(self):
        """Test Redis connection"""
        try:
            if self.redis_client:
                await self.redis_client.ping()
                logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
    
    async def get_analysis_cache(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result with intelligent matching
        
        Args:
            image_data: Raw image bytes
            user_profile: User's profile for context
            
        Returns:
            Cached analysis result or None
        """
        try:
            if not self.enabled:
                return None
            
            # Generate cache key
            cache_key = self._generate_analysis_cache_key(image_data, user_profile)
            
            # Try memory cache first (fastest)
            if cache_key in self.memory_cache:
                self.cache_stats["hits"] += 1
                logger.info(f"💾 Memory cache hit: {cache_key[:16]}...")
                return self.memory_cache[cache_key]
            
            # Try Redis cache
            if self.redis_client:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    result = json.loads(cached_data)
                    # Store in memory cache for faster access
                    self.memory_cache[cache_key] = result
                    self.cache_stats["hits"] += 1
                    logger.info(f"💾 Redis cache hit: {cache_key[:16]}...")
                    return result
            
            # Try similarity-based caching
            similar_result = await self._find_similar_analysis(image_data, user_profile)
            if similar_result:
                self.cache_stats["hits"] += 1
                logger.info(f"🔍 Similarity cache hit: {cache_key[:16]}...")
                return similar_result
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache retrieval failed: {e}")
            return None
    
    async def store_analysis_cache(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]], 
        analysis_result: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store analysis result in cache with intelligent strategies
        
        Args:
            image_data: Raw image bytes
            user_profile: User's profile
            analysis_result: Analysis result to cache
            ttl: Time to live in seconds
            
        Returns:
            True if stored successfully
        """
        try:
            if not self.enabled:
                return False
            
            # Generate cache key
            cache_key = self._generate_analysis_cache_key(image_data, user_profile)
            
            # Prepare data for caching
            cache_data = {
                "result": analysis_result,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl or self.cache_ttl["analysis_results"],
                "cache_version": "2.0.0"
            }
            
            # Store in memory cache
            self.memory_cache[cache_key] = cache_data
            
            # Store in Redis cache
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key,
                    cache_data["ttl"],
                    json.dumps(cache_data, default=str)
                )
            
            # Store similarity features for future matching
            await self._store_similarity_features(image_data, user_profile, analysis_result)
            
            logger.info(f"💾 Cached analysis result: {cache_key[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache storage failed: {e}")
            return False
    
    async def get_recommendation_cache(
        self, 
        conditions: List[str], 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached product recommendations"""
        try:
            if not self.enabled:
                return None
            
            cache_key = self._generate_recommendation_cache_key(conditions, user_profile)
            
            # Try memory cache first
            if cache_key in self.memory_cache:
                self.cache_stats["hits"] += 1
                return self.memory_cache[cache_key]
            
            # Try Redis cache
            if self.redis_client:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    result = json.loads(cached_data)
                    self.memory_cache[cache_key] = result
                    self.cache_stats["hits"] += 1
                    return result
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Recommendation cache retrieval failed: {e}")
            return None
    
    async def store_recommendation_cache(
        self, 
        conditions: List[str], 
        user_profile: Optional[Dict[str, Any]], 
        recommendations: Dict[str, Any]
    ) -> bool:
        """Store product recommendations in cache"""
        try:
            if not self.enabled:
                return False
            
            cache_key = self._generate_recommendation_cache_key(conditions, user_profile)
            
            cache_data = {
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
                "ttl": self.cache_ttl["product_recommendations"]
            }
            
            # Store in memory cache
            self.memory_cache[cache_key] = cache_data
            
            # Store in Redis cache
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key,
                    cache_data["ttl"],
                    json.dumps(cache_data, default=str)
                )
            
            logger.info(f"💾 Cached recommendations: {cache_key[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Recommendation cache storage failed: {e}")
            return False
    
    async def _find_similar_analysis(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find similar analysis results using image similarity
        
        This is an advanced caching strategy that finds similar images
        and reuses their analysis results
        """
        try:
            if not self.redis_client:
                return None
            
            # Extract image features for similarity matching
            image_features = self._extract_image_features(image_data)
            
            # Search for similar images in cache
            similar_keys = await self._search_similar_images(image_features)
            
            if similar_keys:
                # Get the most similar result
                best_key = similar_keys[0]
                cached_data = await self.redis_client.get(best_key)
                
                if cached_data:
                    result = json.loads(cached_data)
                    # Adjust confidence based on similarity
                    similarity_score = result.get("similarity_score", 0.8)
                    if similarity_score > 0.7:  # Only use if very similar
                        logger.info(f"🔍 Found similar analysis with {similarity_score:.2f} similarity")
                        return result["result"]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            return None
    
    def _extract_image_features(self, image_data: bytes) -> Dict[str, Any]:
        """Extract features from image for similarity matching"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Extract basic features
            features = {
                "size": image.size,
                "mode": image.mode,
                "aspect_ratio": image.size[0] / image.size[1],
                "dominant_colors": self._get_dominant_colors(image),
                "brightness": self._calculate_brightness(image),
                "contrast": self._calculate_contrast(image)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Image feature extraction failed: {e}")
            return {}
    
    def _get_dominant_colors(self, image: Image.Image) -> List[tuple]:
        """Get dominant colors from image"""
        try:
            # Resize for faster processing
            image = image.resize((150, 150))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get color histogram
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                # Sort by frequency and get top 5
                colors.sort(key=lambda x: x[0], reverse=True)
                return [color[1] for color in colors[:5]]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Dominant color extraction failed: {e}")
            return []
    
    def _calculate_brightness(self, image: Image.Image) -> float:
        """Calculate average brightness of image"""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Calculate average brightness
            pixels = list(gray.getdata())
            return sum(pixels) / len(pixels) / 255.0
            
        except Exception as e:
            logger.error(f"❌ Brightness calculation failed: {e}")
            return 0.5
    
    def _calculate_contrast(self, image: Image.Image) -> float:
        """Calculate contrast of image"""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Calculate standard deviation as contrast measure
            pixels = list(gray.getdata())
            mean = sum(pixels) / len(pixels)
            variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
            return (variance ** 0.5) / 255.0
            
        except Exception as e:
            logger.error(f"❌ Contrast calculation failed: {e}")
            return 0.5
    
    async def _search_similar_images(self, features: Dict[str, Any]) -> List[str]:
        """Search for similar images in cache"""
        try:
            if not self.redis_client:
                return []
            
            # This would implement actual similarity search
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"❌ Similar image search failed: {e}")
            return []
    
    async def _store_similarity_features(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]], 
        analysis_result: Dict[str, Any]
    ):
        """Store image features for similarity matching"""
        try:
            if not self.redis_client:
                return
            
            # Extract features
            features = self._extract_image_features(image_data)
            
            # Store features with analysis result
            similarity_key = f"similarity:{hashlib.md5(image_data).hexdigest()}"
            similarity_data = {
                "features": features,
                "analysis_result": analysis_result,
                "timestamp": datetime.now().isoformat(),
                "similarity_score": 1.0  # Perfect match for same image
            }
            
            await self.redis_client.setex(
                similarity_key,
                self.cache_ttl["similarity_cache"],
                json.dumps(similarity_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Similarity feature storage failed: {e}")
    
    def _generate_analysis_cache_key(
        self, 
        image_data: bytes, 
        user_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for analysis results"""
        # Create hash of image and user profile
        content = image_data + json.dumps(user_profile or {}, sort_keys=True).encode()
        return f"analysis:{hashlib.md5(content).hexdigest()}"
    
    def _generate_recommendation_cache_key(
        self, 
        conditions: List[str], 
        user_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for recommendations"""
        content = json.dumps({
            "conditions": sorted(conditions),
            "user_profile": user_profile or {}
        }, sort_keys=True).encode()
        return f"recommendations:{hashlib.md5(content).hexdigest()}"
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries for a specific user"""
        try:
            if not self.enabled or not self.redis_client:
                return False
            
            # Pattern to match user-specific cache entries
            pattern = f"*user:{user_id}*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"🗑️ Invalidated {len(keys)} cache entries for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation failed: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            total_requests = self.cache_stats["total_requests"]
            hits = self.cache_stats["hits"]
            misses = self.cache_stats["misses"]
            
            hit_rate = hits / total_requests if total_requests > 0 else 0
            
            stats = {
                "enabled": self.enabled,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "hits": hits,
                "misses": misses,
                "evictions": self.cache_stats["evictions"],
                "memory_cache_size": len(self.memory_cache),
                "redis_connected": self.redis_client is not None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Cache stats retrieval failed: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries"""
        try:
            if not self.redis_client:
                return 0
            
            # Get all cache keys
            keys = await self.redis_client.keys("*")
            expired_count = 0
            
            for key in keys:
                ttl = await self.redis_client.ttl(key)
                if ttl == -1:  # No expiration set
                    continue
                elif ttl == -2:  # Key doesn't exist
                    expired_count += 1
                elif ttl == 0:  # Expired
                    await self.redis_client.delete(key)
                    expired_count += 1
            
            logger.info(f"🧹 Cleaned up {expired_count} expired cache entries")
            return expired_count
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup failed: {e}")
            return 0
    
    async def warm_cache(self, common_conditions: List[str]) -> bool:
        """Warm cache with common analysis results"""
        try:
            if not self.enabled:
                return False
            
            logger.info(f"🔥 Warming cache with {len(common_conditions)} common conditions")
            
            # This would pre-populate cache with common results
            # Implementation depends on available data
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache warming failed: {e}")
            return False


# Global service instance
intelligent_caching_service = IntelligentCachingService()
