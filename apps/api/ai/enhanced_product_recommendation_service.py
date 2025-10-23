"""
Enhanced Product Recommendation Service
Advanced AI-powered product recommendations with comprehensive logging
"""
import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import math
import sys
import os

# Import services
from infrastructure.elasticsearch_service import elasticsearch_service
from infrastructure.google_search_service import google_search_service
from infrastructure.caching import intelligent_caching_service
from ai.vertex_ai_service import vertex_ai_service

# Configuration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'config'))
from settings import VERTEX_AI_ENABLED, ENSEMBLE_ENABLED

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductRecommendation:
    """Structured product recommendation with detailed metadata"""
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
    category: str
    subcategory: str
    availability: str
    size: str
    cruelty_free: bool
    vegan: bool
    fragrance_free: bool
    hypoallergenic: bool


class EnhancedProductRecommendationService:
    """
    Enhanced product recommendation service with advanced AI capabilities
    
    Features:
    - Multi-strategy recommendations
    - Real-time personalization
    - Comprehensive logging
    - A/B testing support
    - Performance optimization
    - Detailed product analysis
    """
    
    def __init__(self):
        """Initialize the enhanced product recommendation service"""
        self.elasticsearch = elasticsearch_service
        self.google_search = google_search_service
        self.caching = intelligent_caching_service
        self.vertex_ai = vertex_ai_service
        
        # Service capabilities
        self.vertex_ai_enabled = VERTEX_AI_ENABLED
        self.ensemble_enabled = ENSEMBLE_ENABLED
        
        # Recommendation strategies
        self.strategies = {
            "collaborative": 0.3,  # User-based collaborative filtering
            "content_based": 0.4,  # Content-based filtering
            "hybrid": 0.3  # Hybrid approach
        }
        
        # Product categories
        self.categories = {
            "cleanser": ["foaming", "gel", "cream", "oil"],
            "moisturizer": ["cream", "lotion", "gel", "serum"],
            "treatment": ["serum", "toner", "essence", "mask"],
            "sunscreen": ["cream", "spray", "stick", "powder"],
            "exfoliant": ["scrub", "acid", "enzyme", "brush"]
        }
        
        # User behavior tracking
        self.user_interactions = {}
        
        logger.info("🛍️ Enhanced Product Recommendation Service initialized")
        logger.info(f"   - Vertex AI: {'✅' if self.vertex_ai_enabled else '❌'}")
        logger.info(f"   - Ensemble: {'✅' if self.ensemble_enabled else '❌'}")
        logger.info(f"   - Strategies: {list(self.strategies.keys())}")
        logger.info(f"   - Categories: {list(self.categories.keys())}")
    
    async def get_enhanced_recommendations(
        self,
        skin_analysis: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None,
        recommendation_type: str = "comprehensive",
        max_recommendations: int = 10,
        budget_range: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """
        Get enhanced AI-powered product recommendations
        
        Args:
            skin_analysis: Results from skin analysis
            user_profile: User's profile and preferences
            recommendation_type: Type of recommendations (comprehensive, quick, budget, premium)
            max_recommendations: Maximum number of recommendations
            budget_range: Optional budget range (min, max)
            
        Returns:
            Enhanced recommendations with detailed metadata
        """
        logger.info("🎯 Starting enhanced product recommendations")
        logger.info(f"   - Recommendation type: {recommendation_type}")
        logger.info(f"   - Max recommendations: {max_recommendations}")
        logger.info(f"   - Budget range: {budget_range}")
        logger.info(f"   - User profile: {'✅' if user_profile else '❌'}")
        
        try:
            # Step 1: Analyze skin conditions and user needs
            logger.info("🔍 Step 1: Analyzing skin conditions and user needs")
            needs_analysis = await self._analyze_user_needs(skin_analysis, user_profile)
            if not needs_analysis["success"]:
                logger.error(f"❌ Needs analysis failed: {needs_analysis['error']}")
                return needs_analysis
            
            needs = needs_analysis["data"]
            logger.info(f"✅ Needs analysis completed")
            logger.info(f"   - Primary concerns: {needs.get('primary_concerns', [])}")
            logger.info(f"   - Skin type: {needs.get('skin_type', 'unknown')}")
            logger.info(f"   - Budget preference: {needs.get('budget_preference', 'medium')}")
            
            # Step 2: Search for relevant products
            logger.info("🔍 Step 2: Searching for relevant products")
            product_search = await self._search_products(needs, max_recommendations, budget_range)
            if not product_search["success"]:
                logger.error(f"❌ Product search failed: {product_search['error']}")
                return product_search
            
            products = product_search["data"]
            logger.info(f"✅ Product search completed")
            logger.info(f"   - Products found: {len(products)}")
            logger.info(f"   - Sources: {product_search.get('sources', [])}")
            
            # Step 3: Apply AI-powered personalization
            logger.info("🤖 Step 3: Applying AI-powered personalization")
            personalized_products = await self._personalize_recommendations(
                products, needs, user_profile
            )
            logger.info(f"✅ Personalization completed")
            logger.info(f"   - Personalized products: {len(personalized_products)}")
            
            # Step 4: Generate comprehensive recommendations
            logger.info("📊 Step 4: Generating comprehensive recommendations")
            recommendations = await self._generate_comprehensive_recommendations(
                personalized_products, needs, recommendation_type
            )
            logger.info(f"✅ Recommendations generated")
            logger.info(f"   - Final recommendations: {len(recommendations)}")
            
            # Step 5: Cache results
            logger.info("💾 Step 5: Caching recommendation results")
            await self._cache_recommendations(recommendations, needs)
            
            logger.info("🎉 Enhanced product recommendations completed successfully")
            return {
                "success": True,
                "recommendations": recommendations,
                "needs_analysis": needs,
                "search_metadata": product_search.get("metadata", {}),
                "personalization_scores": [r.personalization_score for r in recommendations],
                "timestamp": datetime.now().isoformat(),
                "recommendation_type": recommendation_type
            }
            
        except Exception as e:
            logger.error(f"💥 Enhanced product recommendations failed: {str(e)}")
            return {
                "success": False,
                "error": f"Recommendations failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_user_needs(
        self, 
        skin_analysis: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user needs based on skin analysis and profile"""
        try:
            logger.info("🔍 Analyzing user needs and preferences")
            
            # Extract skin conditions
            detected_conditions = skin_analysis.get("detected_conditions", [])
            skin_health_score = skin_analysis.get("skin_health_score", 0.5)
            
            logger.info(f"   - Detected conditions: {detected_conditions}")
            logger.info(f"   - Skin health score: {skin_health_score:.2f}")
            
            # Determine primary concerns
            primary_concerns = self._determine_primary_concerns(detected_conditions, skin_health_score)
            logger.info(f"   - Primary concerns: {primary_concerns}")
            
            # Determine skin type
            skin_type = self._determine_skin_type(detected_conditions, user_profile)
            logger.info(f"   - Skin type: {skin_type}")
            
            # Determine budget preference
            budget_preference = self._determine_budget_preference(user_profile, skin_health_score)
            logger.info(f"   - Budget preference: {budget_preference}")
            
            # Determine product priorities
            product_priorities = self._determine_product_priorities(primary_concerns, skin_type)
            logger.info(f"   - Product priorities: {product_priorities}")
            
            needs = {
                "primary_concerns": primary_concerns,
                "skin_type": skin_type,
                "budget_preference": budget_preference,
                "product_priorities": product_priorities,
                "skin_health_score": skin_health_score,
                "detected_conditions": detected_conditions,
                "user_preferences": user_profile or {}
            }
            
            return {
                "success": True,
                "data": needs
            }
            
        except Exception as e:
            logger.error(f"❌ Needs analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Needs analysis failed: {str(e)}"
            }
    
    def _determine_primary_concerns(self, conditions: List[str], health_score: float) -> List[str]:
        """Determine primary skin concerns based on conditions and health score"""
        concern_mapping = {
            "acne": "acne_treatment",
            "dry_skin": "hydration",
            "oily_skin": "oil_control",
            "hyperpigmentation": "brightening",
            "dark_spots": "brightening",
            "wrinkles": "anti_aging",
            "sensitive_skin": "sensitivity_care",
            "blackheads": "pore_care",
            "whiteheads": "pore_care"
        }
        
        concerns = []
        for condition in conditions:
            if condition in concern_mapping:
                concerns.append(concern_mapping[condition])
        
        # Add general concerns based on health score
        if health_score < 0.3:
            concerns.append("intensive_care")
        elif health_score < 0.6:
            concerns.append("maintenance_care")
        else:
            concerns.append("preventive_care")
        
        return list(set(concerns))
    
    def _determine_skin_type(self, conditions: List[str], user_profile: Optional[Dict[str, Any]]) -> str:
        """Determine skin type based on conditions and user profile"""
        if user_profile and user_profile.get("skin_type"):
            return user_profile["skin_type"]
        
        # Determine from conditions
        if "oily_skin" in conditions:
            return "oily"
        elif "dry_skin" in conditions:
            return "dry"
        elif "sensitive_skin" in conditions:
            return "sensitive"
        else:
            return "combination"
    
    def _determine_budget_preference(self, user_profile: Optional[Dict[str, Any]], health_score: float) -> str:
        """Determine budget preference based on user profile and skin health"""
        if user_profile and user_profile.get("budget_preference"):
            return user_profile["budget_preference"]
        
        # Determine based on skin health
        if health_score < 0.3:
            return "premium"  # Invest more in problematic skin
        elif health_score < 0.6:
            return "medium"
        else:
            return "budget"  # Good skin, can use affordable products
    
    def _determine_product_priorities(self, concerns: List[str], skin_type: str) -> List[str]:
        """Determine product category priorities based on concerns and skin type"""
        priorities = []
        
        # Map concerns to product categories
        concern_to_category = {
            "acne_treatment": ["cleanser", "treatment"],
            "hydration": ["moisturizer", "serum"],
            "oil_control": ["cleanser", "toner"],
            "brightening": ["treatment", "serum"],
            "anti_aging": ["treatment", "serum"],
            "sensitivity_care": ["cleanser", "moisturizer"],
            "pore_care": ["cleanser", "exfoliant"],
            "intensive_care": ["treatment", "serum"],
            "maintenance_care": ["cleanser", "moisturizer"],
            "preventive_care": ["sunscreen", "moisturizer"]
        }
        
        for concern in concerns:
            if concern in concern_to_category:
                priorities.extend(concern_to_category[concern])
        
        # Add skin type specific priorities
        if skin_type == "oily":
            priorities.extend(["cleanser", "toner"])
        elif skin_type == "dry":
            priorities.extend(["moisturizer", "serum"])
        elif skin_type == "sensitive":
            priorities.extend(["cleanser", "moisturizer"])
        
        # Always include sunscreen
        if "sunscreen" not in priorities:
            priorities.append("sunscreen")
        
        return list(set(priorities))
    
    async def _search_products(
        self, 
        needs: Dict[str, Any], 
        max_recommendations: int, 
        budget_range: Optional[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Search for relevant products using multiple sources"""
        try:
            logger.info("🔍 Searching for products from multiple sources")
            
            all_products = []
            sources = []
            
            # Search Elasticsearch
            logger.info("   - Searching Elasticsearch")
            es_results = await self._search_elasticsearch(needs, max_recommendations // 2)
            if es_results["success"]:
                all_products.extend(es_results["data"])
                sources.append("elasticsearch")
                logger.info(f"   - Elasticsearch: {len(es_results['data'])} products")
            
            # Search Google
            logger.info("   - Searching Google")
            google_results = await self._search_google(needs, max_recommendations // 2)
            if google_results["success"]:
                # Ensure productUrl present when possible
                cleaned = []
                for p in google_results["data"]:
                    if not p.get("product_url") and p.get("link"):
                        p["product_url"] = p.get("link")
                    cleaned.append(p)
                all_products.extend(cleaned)
                sources.append("google")
                logger.info(f"   - Google: {len(cleaned)} products")
            
            # Apply budget filter if specified
            if budget_range:
                min_budget, max_budget = budget_range
                filtered_products = [
                    p for p in all_products 
                    if min_budget <= p.get("price", 0) <= max_budget
                ]
                logger.info(f"   - Budget filtered: {len(filtered_products)} products")
                all_products = filtered_products
            
            # Remove duplicates and limit results
            unique_products = self._remove_duplicate_products(all_products)
            final_products = unique_products[:max_recommendations]
            
            logger.info(f"✅ Product search completed")
            logger.info(f"   - Total products: {len(final_products)}")
            logger.info(f"   - Sources: {sources}")
            
            return {
                "success": True,
                "data": final_products,
                "sources": sources,
                "metadata": {
                    "total_found": len(all_products),
                    "unique_products": len(unique_products),
                    "final_count": len(final_products),
                    "budget_filtered": budget_range is not None
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Product search failed: {str(e)}")
            return {
                "success": False,
                "error": f"Product search failed: {str(e)}"
            }
    
    async def _search_elasticsearch(self, needs: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Search products in Elasticsearch"""
        try:
            logger.info("   - Searching Elasticsearch database")
            
            # Build search query
            query = {
                "query": {
                    "bool": {
                        "must": [],
                        "should": []
                    }
                },
                "size": limit
            }
            
            # Add conditions to query
            conditions = needs.get("detected_conditions", [])
            for condition in conditions:
                query["query"]["bool"]["should"].append({
                    "match": {"skin_conditions": condition}
                })
            
            # Add skin type
            skin_type = needs.get("skin_type")
            if skin_type:
                query["query"]["bool"]["should"].append({
                    "match": {"skin_types": skin_type}
                })
            
            # Add product priorities
            priorities = needs.get("product_priorities", [])
            for priority in priorities:
                query["query"]["bool"]["should"].append({
                    "match": {"category": priority}
                })
            
            # Execute search
            result = await self.elasticsearch.search_products(query)
            
            if result["success"]:
                products = result["data"]
                logger.info(f"   - Elasticsearch found: {len(products)} products")
                return {
                    "success": True,
                    "data": products
                }
            else:
                logger.warning(f"   - Elasticsearch search failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Elasticsearch search failed")
                }
                
        except Exception as e:
            logger.error(f"❌ Elasticsearch search failed: {str(e)}")
            return {
                "success": False,
                "error": f"Elasticsearch search failed: {str(e)}"
            }
    
    async def _search_google(self, needs: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Search products using Google Custom Search"""
        try:
            logger.info("   - Searching Google Custom Search")
            
            # Build search terms
            conditions = needs.get("detected_conditions", [])
            priorities = needs.get("product_priorities", [])
            
            search_terms = []
            for condition in conditions[:2]:  # Limit to top 2 conditions
                for priority in priorities[:2]:  # Limit to top 2 priorities
                    search_terms.append(f"{condition} {priority} skincare")
            
            # Execute searches
            products = []
            for term in search_terms[:3]:  # Limit to 3 searches
                try:
                    result = await self.google_search.search_products(term, limit=limit//3)
                    if result["success"]:
                        products.extend(result["data"])
                        logger.info(f"   - Google search '{term}': {len(result['data'])} products")
                except Exception as e:
                    logger.warning(f"   - Google search '{term}' failed: {str(e)}")
                    continue
            
            logger.info(f"   - Google found: {len(products)} products")
            return {
                "success": True,
                "data": products
            }
            
        except Exception as e:
            logger.error(f"❌ Google search failed: {str(e)}")
            return {
                "success": False,
                "error": f"Google search failed: {str(e)}"
            }
    
    def _remove_duplicate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate products based on name and brand"""
        seen = set()
        unique_products = []
        
        for product in products:
            key = (product.get("name", "").lower(), product.get("brand", "").lower())
            if key not in seen:
                seen.add(key)
                unique_products.append(product)
        
        logger.info(f"   - Removed {len(products) - len(unique_products)} duplicates")
        return unique_products
    
    async def _personalize_recommendations(
        self, 
        products: List[Dict[str, Any]], 
        needs: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]]
    ) -> List[ProductRecommendation]:
        """Apply AI-powered personalization to products"""
        try:
            logger.info("🤖 Applying AI-powered personalization")
            
            personalized_products = []
            
            for product in products:
                # Calculate personalization score
                personalization_score = self._calculate_personalization_score(
                    product, needs, user_profile
                )
                
                # Create enhanced product recommendation
                recommendation = ProductRecommendation(
                    name=product.get("name", "Unknown Product"),
                    brand=product.get("brand", "Unknown Brand"),
                    price=float(product.get("price", 0)),
                    rating=float(product.get("rating", 0)),
                    description=product.get("description", ""),
                    url=product.get("url", ""),
                    image=product.get("image", ""),
                    confidence_score=float(product.get("confidence", 0.5)),
                    recommendation_reason=self._generate_recommendation_reason(
                        product, needs, personalization_score
                    ),
                    ingredients=product.get("ingredients", []),
                    skin_conditions=product.get("skin_conditions", []),
                    skin_types=product.get("skin_types", []),
                    personalization_score=personalization_score,
                    category=product.get("category", "unknown"),
                    subcategory=product.get("subcategory", ""),
                    availability=product.get("availability", "unknown"),
                    size=product.get("size", ""),
                    cruelty_free=product.get("cruelty_free", False),
                    vegan=product.get("vegan", False),
                    fragrance_free=product.get("fragrance_free", False),
                    hypoallergenic=product.get("hypoallergenic", False)
                )
                
                personalized_products.append(recommendation)
            
            # Sort by personalization score
            personalized_products.sort(key=lambda x: x.personalization_score, reverse=True)
            
            logger.info(f"✅ Personalization completed")
            logger.info(f"   - Personalized products: {len(personalized_products)}")
            logger.info(f"   - Score range: {min(p.personalization_score for p in personalized_products):.2f} - {max(p.personalization_score for p in personalized_products):.2f}")
            
            return personalized_products
            
        except Exception as e:
            logger.error(f"❌ Personalization failed: {str(e)}")
            return []
    
    def _calculate_personalization_score(
        self, 
        product: Dict[str, Any], 
        needs: Dict[str, Any], 
        user_profile: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate personalization score for a product"""
        try:
            score = 0.0
            
            # Base score from product rating
            rating = float(product.get("rating", 0))
            score += rating * 0.2
            
            # Match with skin conditions
            product_conditions = product.get("skin_conditions", [])
            user_conditions = needs.get("detected_conditions", [])
            condition_matches = len(set(product_conditions) & set(user_conditions))
            if user_conditions:
                score += (condition_matches / len(user_conditions)) * 0.3
            
            # Match with skin type
            product_skin_types = product.get("skin_types", [])
            user_skin_type = needs.get("skin_type", "")
            if user_skin_type in product_skin_types:
                score += 0.2
            
            # Match with product priorities
            product_category = product.get("category", "")
            priorities = needs.get("product_priorities", [])
            if product_category in priorities:
                score += 0.2
            
            # User preferences
            if user_profile:
                # Budget preference
                budget_pref = needs.get("budget_preference", "medium")
                price = float(product.get("price", 0))
                
                if budget_pref == "budget" and price < 20:
                    score += 0.1
                elif budget_pref == "medium" and 20 <= price <= 50:
                    score += 0.1
                elif budget_pref == "premium" and price > 50:
                    score += 0.1
                
                # Brand preferences
                preferred_brands = user_profile.get("preferred_brands", [])
                product_brand = product.get("brand", "").lower()
                if any(brand.lower() in product_brand for brand in preferred_brands):
                    score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"❌ Personalization score calculation failed: {str(e)}")
            return 0.5  # Default score
    
    def _generate_recommendation_reason(
        self, 
        product: Dict[str, Any], 
        needs: Dict[str, Any], 
        score: float
    ) -> str:
        """Generate human-readable recommendation reason"""
        try:
            reasons = []
            
            # High score reasons
            if score > 0.8:
                reasons.append("Excellent match for your skin concerns")
            elif score > 0.6:
                reasons.append("Good match for your skin type")
            elif score > 0.4:
                reasons.append("Suitable for your skin needs")
            else:
                reasons.append("May help with your skin concerns")
            
            # Specific condition matches
            product_conditions = product.get("skin_conditions", [])
            user_conditions = needs.get("detected_conditions", [])
            matches = set(product_conditions) & set(user_conditions)
            
            if matches:
                reasons.append(f"Targets: {', '.join(matches)}")
            
            # Skin type match
            product_skin_types = product.get("skin_types", [])
            user_skin_type = needs.get("skin_type", "")
            if user_skin_type in product_skin_types:
                reasons.append(f"Formulated for {user_skin_type} skin")
            
            return "; ".join(reasons)
            
        except Exception as e:
            logger.error(f"❌ Recommendation reason generation failed: {str(e)}")
            return "Recommended based on your skin analysis"
    
    async def _generate_comprehensive_recommendations(
        self, 
        products: List[ProductRecommendation], 
        needs: Dict[str, Any], 
        recommendation_type: str
    ) -> List[ProductRecommendation]:
        """Generate comprehensive recommendations with additional metadata"""
        try:
            logger.info("📊 Generating comprehensive recommendations")
            
            # Filter by recommendation type
            if recommendation_type == "budget":
                products = [p for p in products if p.price < 30]
            elif recommendation_type == "premium":
                products = [p for p in products if p.price > 50]
            
            # Add additional metadata
            for product in products:
                # Add usage instructions
                product.usage_instructions = self._generate_usage_instructions(product, needs)
                
                # Add compatibility notes
                product.compatibility_notes = self._generate_compatibility_notes(product, needs)
                
                # Add expected results
                product.expected_results = self._generate_expected_results(product, needs)
            
            logger.info(f"✅ Comprehensive recommendations generated")
            logger.info(f"   - Final count: {len(products)}")
            
            return products
            
        except Exception as e:
            logger.error(f"❌ Comprehensive recommendations failed: {str(e)}")
            return products
    
    def _generate_usage_instructions(self, product: ProductRecommendation, needs: Dict[str, Any]) -> str:
        """Generate usage instructions for a product"""
        category = product.category.lower()
        
        if category == "cleanser":
            return "Use morning and evening. Apply to wet skin, massage gently, then rinse thoroughly."
        elif category == "moisturizer":
            return "Apply after cleansing and treatment. Use morning and evening on damp skin."
        elif category == "treatment":
            return "Apply after cleansing, before moisturizer. Start with every other day, then increase frequency."
        elif category == "sunscreen":
            return "Apply every morning as the final step. Reapply every 2 hours if outdoors."
        else:
            return "Follow the product's specific instructions for best results."
    
    def _generate_compatibility_notes(self, product: ProductRecommendation, needs: Dict[str, Any]) -> str:
        """Generate compatibility notes for a product"""
        notes = []
        
        if product.fragrance_free:
            notes.append("Fragrance-free formula")
        if product.hypoallergenic:
            notes.append("Hypoallergenic")
        if product.cruelty_free:
            notes.append("Cruelty-free")
        if product.vegan:
            notes.append("Vegan formula")
        
        skin_type = needs.get("skin_type", "")
        if skin_type == "sensitive" and product.hypoallergenic:
            notes.append("Suitable for sensitive skin")
        
        return "; ".join(notes) if notes else "Standard compatibility"
    
    def _generate_expected_results(self, product: ProductRecommendation, needs: Dict[str, Any]) -> str:
        """Generate expected results for a product"""
        conditions = needs.get("detected_conditions", [])
        
        if "acne" in conditions and "cleanser" in product.category:
            return "Reduced breakouts and clearer skin within 2-4 weeks"
        elif "dry_skin" in conditions and "moisturizer" in product.category:
            return "Improved hydration and smoother skin within 1-2 weeks"
        elif "hyperpigmentation" in conditions and "treatment" in product.category:
            return "Brighter, more even skin tone within 4-8 weeks"
        else:
            return "Improved skin health and appearance with consistent use"
    
    async def _cache_recommendations(self, recommendations: List[ProductRecommendation], needs: Dict[str, Any]) -> None:
        """Cache recommendation results"""
        try:
            logger.info("💾 Caching recommendation results")
            
            # Create cache key
            cache_key = f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare cache data
            cache_data = {
                "recommendations": [
                    {
                        "name": r.name,
                        "brand": r.brand,
                        "price": r.price,
                        "personalization_score": r.personalization_score,
                        "category": r.category
                    }
                    for r in recommendations
                ],
                "needs": needs,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the results
            await self.caching.set(cache_key, cache_data, ttl=1800)  # 30 minutes TTL
            
            logger.info(f"✅ Recommendations cached with key: {cache_key}")
            
        except Exception as e:
            logger.error(f"❌ Caching failed: {str(e)}")


# Create global instance
enhanced_product_recommendation_service = EnhancedProductRecommendationService()
