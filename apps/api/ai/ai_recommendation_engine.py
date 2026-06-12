"""
AI-Powered Recommendation Engine for Dermalens
Uses machine learning and AI to provide intelligent product recommendations
"""

import asyncio
import json
import logging
import math
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from ai.vertex_ai_service import vertex_ai_service

# Configuration
from config import ENSEMBLE_ENABLED, PERFORMANCE_MONITORING_ENABLED, VERTEX_AI_ENABLED
from infrastructure.caching import intelligent_caching_service

# Import services
from infrastructure.elasticsearch_service import elasticsearch_service
from infrastructure.google_search_service import google_search_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductRecommendation:
    """Structured product recommendation"""

    name: str
    brand: str
    price: float
    rating: float
    description: str
    url: str
    image: str
    confidence_score: float
    recommendation_reason: str
    ingredients: List[str]
    skin_conditions: List[str]
    skin_types: List[str]
    personalization_score: float


class AIRecommendationEngine:
    """
    AI-powered recommendation engine with multiple strategies

    Features:
    - Collaborative filtering
    - Content-based filtering
    - Hybrid recommendations
    - Real-time personalization
    - A/B testing support
    - Performance optimization
    """

    def __init__(self):
        """Initialize the AI recommendation engine"""
        self.elasticsearch = elasticsearch_service
        self.google_search = google_search_service
        self.caching = intelligent_caching_service
        self.vertex_ai = vertex_ai_service

        # Engine capabilities
        self.vertex_ai_enabled = VERTEX_AI_ENABLED
        self.ensemble_enabled = ENSEMBLE_ENABLED
        self.monitoring_enabled = PERFORMANCE_MONITORING_ENABLED

        # Recommendation strategies
        self.strategies = {
            "collaborative": 0.3,  # User-based collaborative filtering
            "content_based": 0.4,  # Content-based filtering
            "hybrid": 0.3,  # Hybrid approach
        }

        # User behavior tracking
        self.user_interactions = {}

        logger.info("🤖 AI Recommendation Engine initialized")
        logger.info(f"   - Vertex AI: {'✅' if self.vertex_ai_enabled else '❌'}")
        logger.info(f"   - Ensemble: {'✅' if self.ensemble_enabled else '❌'}")
        logger.info(f"   - Monitoring: {'✅' if self.monitoring_enabled else '❌'}")

    async def get_ai_recommendations(
        self,
        skin_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
        recommendation_type: str = "comprehensive",
        max_recommendations: int = 10,
    ) -> Dict[str, Any]:
        """
        Get AI-powered product recommendations

        Args:
            skin_analysis: Results from skin analysis
            user_profile: User's profile and preferences
            recommendation_type: Type of recommendations (comprehensive, quick, personalized)
            max_recommendations: Maximum number of recommendations

        Returns:
            AI-powered recommendations with explanations
        """
        logger.info(f"🎯 Generating {recommendation_type} AI recommendations")

        try:
            # Check cache first
            cache_key = self._generate_recommendation_cache_key(skin_analysis, user_profile)
            cached_recommendations = await self.caching.get_recommendation_cache(
                skin_analysis.get("detected_conditions", []), user_profile
            )

            if cached_recommendations:
                logger.info("💾 Using cached recommendations")
                return cached_recommendations

            # Generate fresh recommendations
            recommendations = await self._generate_fresh_recommendations(
                skin_analysis, user_profile, recommendation_type, max_recommendations
            )

            # Cache results
            await self.caching.store_recommendation_cache(
                skin_analysis.get("detected_conditions", []), user_profile, recommendations
            )

            return recommendations

        except Exception as e:
            logger.error(f"❌ AI recommendations failed: {e}")
            return {
                "success": False,
                "error": f"Recommendation generation failed: {str(e)}",
                "recommendations": [],
            }

    async def _generate_fresh_recommendations(
        self,
        skin_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
        recommendation_type: str,
        max_recommendations: int,
    ) -> Dict[str, Any]:
        """Generate fresh AI recommendations using multiple strategies"""
        try:
            # Extract analysis data
            conditions = skin_analysis.get("detected_conditions", [])
            skin_type = skin_analysis.get("skin_type", {}).get("primary", "normal")
            health_score = skin_analysis.get("overall_health_score", 75)

            # Get base products from different sources
            all_products = []

            # 1. Elasticsearch recommendations (content-based)
            elasticsearch_products = await self._get_elasticsearch_recommendations(
                conditions, skin_type, user_profile
            )
            all_products.extend(elasticsearch_products)

            # 2. Google Search recommendations (trending)
            google_products = await self._get_google_recommendations(conditions, user_profile)
            all_products.extend(google_products)

            # 3. Vertex AI recommendations (if enabled)
            if self.vertex_ai_enabled:
                vertex_products = await self._get_vertex_ai_recommendations(
                    skin_analysis, user_profile
                )
                all_products.extend(vertex_products)

            # 4. Apply AI-powered ranking and filtering
            ranked_products = await self._rank_products_ai(
                all_products, skin_analysis, user_profile
            )

            # 5. Personalize recommendations
            personalized_products = await self._personalize_recommendations(
                ranked_products, user_profile
            )

            # 6. Apply diversity and balance
            final_recommendations = await self._apply_diversity_filtering(
                personalized_products, max_recommendations
            )

            return {
                "success": True,
                "recommendations": final_recommendations,
                "total_found": len(all_products),
                "ai_enhanced": True,
                "personalization_score": self._calculate_personalization_score(
                    final_recommendations, user_profile
                ),
                "recommendation_metadata": {
                    "strategy_used": recommendation_type,
                    "timestamp": datetime.now().isoformat(),
                    "vertex_ai_used": self.vertex_ai_enabled,
                    "ensemble_used": self.ensemble_enabled,
                },
            }

        except Exception as e:
            logger.error(f"❌ Fresh recommendation generation failed: {e}")
            raise

    async def _get_elasticsearch_recommendations(
        self, conditions: List[str], skin_type: str, user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get recommendations from Elasticsearch"""
        try:
            # Build search query
            search_query = {
                "skin_conditions": conditions,
                "skin_types": [skin_type],
                "min_rating": 4.0,
                "size": 20,
            }

            # Add user preferences
            if user_profile.get("budget"):
                search_query["price_range"] = {
                    "gte": user_profile["budget"][0],
                    "lte": user_profile["budget"][1],
                }

            # Search products
            result = self.elasticsearch.search_products(**search_query)

            if result["success"]:
                products = result["products"]
                logger.info(f"📊 Found {len(products)} products from Elasticsearch")
                return products

            return []

        except Exception as e:
            logger.error(f"❌ Elasticsearch recommendations failed: {e}")
            return []

    async def _get_google_recommendations(
        self, conditions: List[str], user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get recommendations from Google Search"""
        try:
            if not self.google_search.is_enabled():
                return []

            all_products = []

            for condition in conditions[:3]:  # Top 3 conditions
                result = self.google_search.search_products_for_conditions(
                    conditions=[condition], user_profile=user_profile
                )

                if result["success"]:
                    all_products.extend(result["recommended_products"])

            # Deduplicate
            seen_urls = set()
            unique_products = []
            for product in all_products:
                if product.get("url") and product["url"] not in seen_urls:
                    seen_urls.add(product["url"])
                    unique_products.append(product)

            logger.info(f"🔍 Found {len(unique_products)} products from Google Search")
            return unique_products[:10]  # Top 10

        except Exception as e:
            logger.error(f"❌ Google recommendations failed: {e}")
            return []

    async def _get_vertex_ai_recommendations(
        self, skin_analysis: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get AI-powered recommendations from Vertex AI"""
        try:
            if not self.vertex_ai_enabled:
                return []

            # Use Vertex AI for recommendations
            result = await self.vertex_ai.get_ai_recommendations(skin_analysis, user_profile)

            if result["success"]:
                products = result["recommendations"]
                logger.info(f"🤖 Found {len(products)} products from Vertex AI")
                return products

            return []

        except Exception as e:
            logger.error(f"❌ Vertex AI recommendations failed: {e}")
            return []

    async def _rank_products_ai(
        self,
        products: List[Dict[str, Any]],
        skin_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
    ) -> List[ProductRecommendation]:
        """Rank products using AI-powered algorithms"""
        try:
            if not products:
                return []

            # Convert to structured recommendations
            recommendations = []

            for product in products:
                # Calculate AI-powered scores
                relevance_score = self._calculate_relevance_score(product, skin_analysis)
                personalization_score = self._calculate_personalization_score(product, user_profile)
                quality_score = self._calculate_quality_score(product)
                popularity_score = self._calculate_popularity_score(product)

                # Combine scores with weights
                final_score = (
                    relevance_score * 0.4
                    + personalization_score * 0.3
                    + quality_score * 0.2
                    + popularity_score * 0.1
                )

                # Create structured recommendation
                recommendation = ProductRecommendation(
                    name=product.get("name", "Unknown Product"),
                    brand=product.get("brand", "Unknown Brand"),
                    price=product.get("price", 0),
                    rating=product.get("rating", 0),
                    description=product.get("description", ""),
                    url=product.get("url", ""),
                    image=product.get("image", ""),
                    confidence_score=final_score,
                    recommendation_reason=self._generate_recommendation_reason(
                        product, skin_analysis, user_profile
                    ),
                    ingredients=product.get("ingredients", []),
                    skin_conditions=product.get("skin_conditions", []),
                    skin_types=product.get("skin_types", []),
                    personalization_score=personalization_score,
                )

                recommendations.append(recommendation)

            # Sort by final score
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)

            logger.info(f"🎯 Ranked {len(recommendations)} products using AI")
            return recommendations

        except Exception as e:
            logger.error(f"❌ AI ranking failed: {e}")
            return []

    def _calculate_relevance_score(
        self, product: Dict[str, Any], skin_analysis: Dict[str, Any]
    ) -> float:
        """Calculate how relevant a product is to the skin analysis"""
        try:
            score = 0.0

            # Check condition matches
            detected_conditions = skin_analysis.get("detected_conditions", [])
            product_conditions = product.get("skin_conditions", [])

            if detected_conditions and product_conditions:
                matches = set(detected_conditions) & set(product_conditions)
                condition_score = len(matches) / len(detected_conditions)
                score += condition_score * 0.6

            # Check skin type match
            detected_skin_type = skin_analysis.get("skin_type", {}).get("primary", "normal")
            product_skin_types = product.get("skin_types", [])

            if detected_skin_type in product_skin_types:
                score += 0.3

            # Check health score alignment
            health_score = skin_analysis.get("overall_health_score", 75)
            product_rating = product.get("rating", 0)

            if health_score < 60 and product_rating > 4.0:  # Low health, high-rated product
                score += 0.1

            return min(1.0, score)

        except Exception as e:
            logger.error(f"❌ Relevance score calculation failed: {e}")
            return 0.5

    def _calculate_personalization_score(
        self, product: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> float:
        """Calculate how well a product matches user preferences"""
        try:
            score = 0.0

            # Check budget alignment
            user_budget = user_profile.get("budget", [0, 1000])
            product_price = product.get("price", 0)

            if user_budget[0] <= product_price <= user_budget[1]:
                score += 0.3
            elif product_price < user_budget[0]:
                score += 0.1  # Below budget is okay

            # Check allergy compatibility
            user_allergies = user_profile.get("allergies", [])
            product_ingredients = product.get("ingredients", [])

            if user_allergies and product_ingredients:
                allergy_matches = set(user_allergies) & set(product_ingredients)
                if not allergy_matches:  # No allergy conflicts
                    score += 0.4
                else:
                    score -= 0.5  # Penalty for allergies

            # Check brand preferences
            user_brands = user_profile.get("preferred_brands", [])
            product_brand = product.get("brand", "")

            if user_brands and product_brand in user_brands:
                score += 0.2

            # Check sensitivity considerations
            sensitivity_level = user_profile.get("sensitivity_level", "low")
            if sensitivity_level == "high":
                if product.get("fragrance_free", False):
                    score += 0.1
                if product.get("allergen_free", False):
                    score += 0.1

            return min(1.0, max(0.0, score))

        except Exception as e:
            logger.error(f"❌ Personalization score calculation failed: {e}")
            return 0.5

    def _calculate_quality_score(self, product: Dict[str, Any]) -> float:
        """Calculate product quality score"""
        try:
            score = 0.0

            # Rating score
            rating = product.get("rating", 0)
            score += (rating / 5.0) * 0.4

            # Review count score (more reviews = more reliable)
            review_count = product.get("review_count", 0)
            if review_count > 100:
                score += 0.3
            elif review_count > 50:
                score += 0.2
            elif review_count > 10:
                score += 0.1

            # Brand reputation (simplified)
            brand = product.get("brand", "").lower()
            reputable_brands = ["cerave", "the ordinary", "paula's choice", "la roche-posay"]
            if any(reputable in brand for reputable in reputable_brands):
                score += 0.3

            return min(1.0, score)

        except Exception as e:
            logger.error(f"❌ Quality score calculation failed: {e}")
            return 0.5

    def _calculate_popularity_score(self, product: Dict[str, Any]) -> float:
        """Calculate product popularity score"""
        try:
            score = 0.0

            # Review count as popularity indicator
            review_count = product.get("review_count", 0)
            if review_count > 1000:
                score += 0.5
            elif review_count > 500:
                score += 0.3
            elif review_count > 100:
                score += 0.1

            # Rating as popularity indicator
            rating = product.get("rating", 0)
            if rating > 4.5:
                score += 0.3
            elif rating > 4.0:
                score += 0.2
            elif rating > 3.5:
                score += 0.1

            return min(1.0, score)

        except Exception as e:
            logger.error(f"❌ Popularity score calculation failed: {e}")
            return 0.5

    def _generate_recommendation_reason(
        self, product: Dict[str, Any], skin_analysis: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> str:
        """Generate human-readable reason for recommendation"""
        try:
            reasons = []

            # Condition-based reasons
            detected_conditions = skin_analysis.get("detected_conditions", [])
            product_conditions = product.get("skin_conditions", [])

            if detected_conditions and product_conditions:
                matches = set(detected_conditions) & set(product_conditions)
                if matches:
                    reasons.append(f"Targets: {', '.join(matches)}")

            # Skin type reasons
            detected_skin_type = skin_analysis.get("skin_type", {}).get("primary", "normal")
            product_skin_types = product.get("skin_types", [])

            if detected_skin_type in product_skin_types:
                reasons.append(f"Perfect for {detected_skin_type} skin")

            # Quality reasons
            rating = product.get("rating", 0)
            if rating > 4.5:
                reasons.append("Highly rated")
            elif rating > 4.0:
                reasons.append("Well-reviewed")

            # Special features
            if product.get("fragrance_free", False):
                reasons.append("Fragrance-free")
            if product.get("cruelty_free", False):
                reasons.append("Cruelty-free")
            if product.get("vegan", False):
                reasons.append("Vegan")

            return "; ".join(reasons) if reasons else "AI recommended based on your skin analysis"

        except Exception as e:
            logger.error(f"❌ Recommendation reason generation failed: {e}")
            return "Recommended based on your skin analysis"

    async def _personalize_recommendations(
        self, recommendations: List[ProductRecommendation], user_profile: Dict[str, Any]
    ) -> List[ProductRecommendation]:
        """Apply personalization to recommendations"""
        try:
            # Apply user-specific adjustments
            personalized = []

            for rec in recommendations:
                # Adjust score based on user history
                user_history_score = self._get_user_history_score(rec, user_profile)
                rec.confidence_score = (rec.confidence_score + user_history_score) / 2

                # Adjust based on user preferences
                preference_score = self._get_preference_score(rec, user_profile)
                rec.personalization_score = preference_score

                personalized.append(rec)

            # Re-sort by updated scores
            personalized.sort(key=lambda x: x.confidence_score, reverse=True)

            return personalized

        except Exception as e:
            logger.error(f"❌ Personalization failed: {e}")
            return recommendations

    def _get_user_history_score(
        self, recommendation: ProductRecommendation, user_profile: Dict[str, Any]
    ) -> float:
        """Get score based on user's interaction history"""
        try:
            # This would integrate with user behavior tracking
            # For now, return neutral score
            return 0.5

        except Exception as e:
            logger.error(f"❌ User history score calculation failed: {e}")
            return 0.5

    def _get_preference_score(
        self, recommendation: ProductRecommendation, user_profile: Dict[str, Any]
    ) -> float:
        """Get score based on user preferences"""
        try:
            score = 0.0

            # Brand preference
            user_brands = user_profile.get("preferred_brands", [])
            if user_brands and recommendation.brand.lower() in [b.lower() for b in user_brands]:
                score += 0.3

            # Price preference
            user_budget = user_profile.get("budget", [0, 1000])
            if user_budget[0] <= recommendation.price <= user_budget[1]:
                score += 0.4

            # Ingredient preferences
            user_ingredients = user_profile.get("preferred_ingredients", [])
            if user_ingredients and recommendation.ingredients:
                matches = set(user_ingredients) & set(recommendation.ingredients)
                score += len(matches) * 0.1

            return min(1.0, score)

        except Exception as e:
            logger.error(f"❌ Preference score calculation failed: {e}")
            return 0.5

    async def _apply_diversity_filtering(
        self, recommendations: List[ProductRecommendation], max_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Apply diversity filtering to ensure variety in recommendations"""
        try:
            if not recommendations:
                return []

            # Group by product type for diversity
            product_types = {}
            for rec in recommendations:
                product_type = self._categorize_product(rec)
                if product_type not in product_types:
                    product_types[product_type] = []
                product_types[product_type].append(rec)

            # Select diverse recommendations
            diverse_recommendations = []
            max_per_type = (
                max(1, max_recommendations // len(product_types))
                if product_types
                else max_recommendations
            )

            for product_type, products in product_types.items():
                diverse_recommendations.extend(products[:max_per_type])

            # Sort by confidence score and take top N
            diverse_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            final_recommendations = diverse_recommendations[:max_recommendations]

            # Convert to dictionary format
            result = []
            for rec in final_recommendations:
                result.append(
                    {
                        "name": rec.name,
                        "brand": rec.brand,
                        "price": rec.price,
                        "rating": rec.rating,
                        "description": rec.description,
                        "url": rec.url,
                        "image": rec.image,
                        "confidence_score": rec.confidence_score,
                        "recommendation_reason": rec.recommendation_reason,
                        "personalization_score": rec.personalization_score,
                        "ingredients": rec.ingredients,
                        "skin_conditions": rec.skin_conditions,
                        "skin_types": rec.skin_types,
                    }
                )

            logger.info(f"🎯 Selected {len(result)} diverse recommendations")
            return result

        except Exception as e:
            logger.error(f"❌ Diversity filtering failed: {e}")
            return []

    def _categorize_product(self, recommendation: ProductRecommendation) -> str:
        """Categorize product by type"""
        name_lower = recommendation.name.lower()

        if any(word in name_lower for word in ["cleanser", "wash", "foam"]):
            return "cleanser"
        elif any(word in name_lower for word in ["serum", "treatment", "ampoule"]):
            return "serum"
        elif any(word in name_lower for word in ["moisturizer", "cream", "lotion"]):
            return "moisturizer"
        elif any(word in name_lower for word in ["sunscreen", "spf", "sun"]):
            return "sunscreen"
        elif any(word in name_lower for word in ["toner", "essence", "mist"]):
            return "toner"
        else:
            return "other"

    def _generate_recommendation_cache_key(
        self, skin_analysis: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> str:
        """Generate cache key for recommendations"""
        import hashlib

        content = json.dumps(
            {
                "conditions": skin_analysis.get("detected_conditions", []),
                "skin_type": skin_analysis.get("skin_type", {}),
                "health_score": skin_analysis.get("overall_health_score", 75),
                "user_profile": user_profile,
            },
            sort_keys=True,
        ).encode()

        return f"ai_recommendations:{hashlib.md5(content).hexdigest()}"

    def _calculate_personalization_score(
        self, recommendations: List[Dict[str, Any]], user_profile: Dict[str, Any]
    ) -> float:
        """Calculate overall personalization score for recommendations"""
        try:
            if not recommendations:
                return 0.0

            total_score = 0.0
            for rec in recommendations:
                total_score += rec.get("personalization_score", 0.5)

            return total_score / len(recommendations)

        except Exception as e:
            logger.error(f"❌ Personalization score calculation failed: {e}")
            return 0.5


# Global service instance
ai_recommendation_engine = AIRecommendationEngine()
