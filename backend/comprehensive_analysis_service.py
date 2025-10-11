"""
Comprehensive skin analysis service integrating:
- Supabase user data and images
- OpenAI Vision API for diagnosis
- Google Custom Search for product recommendations
"""
from typing import Dict, Optional, Any
import logging
import requests
from database import db_manager
from openai_analysis_service import openai_analysis_service
from google_search_service import google_search_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveSkinAnalysisService:
    """Service that orchestrates complete skin analysis workflow"""
    
    def __init__(self):
        self.db = db_manager
        self.ai = openai_analysis_service
        self.search = google_search_service
    
    async def analyze_user_by_id(
        self,
        user_id: str,
        image_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete analysis workflow:
        1. Fetch user profile and skin profile from Supabase
        2. Fetch user's face image from Supabase
        3. Analyze image with OpenAI Vision API
        4. Search for products with Google Custom Search
        5. Generate personalized recommendations
        
        Args:
            user_id: User's ID in Supabase
            image_id: Specific image ID to analyze (optional, uses latest if not provided)
            
        Returns:
            Complete analysis with recommendations and products
        """
        logger.info(f"Starting comprehensive analysis for user: {user_id}")
        
        try:
            # Step 1: Fetch user profile
            profile_result = await self.db.get_profile(user_id)
            if not profile_result["success"]:
                return {
                    "success": False,
                    "error": "User profile not found",
                    "step_failed": "fetch_profile"
                }
            
            user_profile = profile_result["data"]
            logger.info(f"Fetched profile for user: {user_profile.get('username', 'unknown')}")
            
            # Step 2: Fetch user skin profile
            skin_profile_result = await self.db.get_skin_profile(user_id)
            user_skin_profile = skin_profile_result["data"] if skin_profile_result["success"] else None
            
            if user_skin_profile:
                logger.info(f"Fetched skin profile with {len(user_skin_profile.get('allergies', []))} allergies")
            
            # Step 3: Fetch user's images
            images_result = await self.db.get_user_images(user_id)
            if not images_result["success"] or not images_result["data"]:
                return {
                    "success": False,
                    "error": "No images found for this user. Please upload a face image first.",
                    "step_failed": "fetch_images"
                }
            
            # Get the image to analyze (specific or latest)
            user_images = images_result["data"]
            if image_id:
                image_to_analyze = next((img for img in user_images if img["id"] == image_id), None)
                if not image_to_analyze:
                    return {
                        "success": False,
                        "error": f"Image with ID {image_id} not found",
                        "step_failed": "select_image"
                    }
            else:
                # Use the most recent image
                image_to_analyze = user_images[0]
            
            logger.info(f"Selected image: {image_to_analyze['storage_path']}")
            
            # Step 4: Download image from Supabase Storage
            image_data = await self._download_image_from_supabase(
                image_to_analyze["bucket"],
                image_to_analyze["storage_path"]
            )
            
            if not image_data:
                return {
                    "success": False,
                    "error": "Failed to download image from storage",
                    "step_failed": "download_image"
                }
            
            # Step 5: Analyze image with OpenAI Vision API
            logger.info("Analyzing image with OpenAI Vision API...")
            analysis_result = self.ai.analyze_skin_image(
                image_data=image_data,
                user_profile=user_profile,
                user_skin_profile=user_skin_profile
            )
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": f"AI analysis failed: {analysis_result.get('error')}",
                    "step_failed": "ai_analysis"
                }
            
            logger.info(f"AI detected {len(analysis_result['analysis']['conditions_detected'])} skin conditions")
            
            # Step 6: Generate personalized recommendations
            recommendations = self.ai.generate_personalized_recommendations(
                analysis_result,
                user_skin_profile
            )
            
            # Step 7: Search for real products using Google Custom Search
            logger.info("Searching for products with Google Custom Search...")
            products = await self._search_products_for_recommendations(
                recommendations,
                user_skin_profile
            )
            
            # Step 8: Generate actionable routine
            routine = self._generate_skincare_routine(
                analysis_result["analysis"],
                products,
                user_skin_profile
            )
            
            # Return comprehensive results
            return {
                "success": True,
                "user_profile": {
                    "username": user_profile.get("username"),
                    "email": user_profile.get("email")
                },
                "skin_profile": user_skin_profile,
                "ai_analysis": {
                    "conditions_detected": analysis_result["analysis"]["conditions_detected"],
                    "skin_type": analysis_result["analysis"]["skin_type"],
                    "recommended_ingredients": analysis_result["analysis"]["recommended_ingredients"],
                    "recommended_products": analysis_result["analysis"]["recommended_product_types"],
                    "full_diagnosis": analysis_result["analysis"]["full_analysis"],
                    "model_used": analysis_result["model_used"]
                },
                "product_recommendations": products,
                "personalized_routine": routine,
                "image_analyzed": {
                    "id": image_to_analyze["id"],
                    "path": image_to_analyze["storage_path"],
                    "analyzed_at": image_to_analyze["created_at"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "step_failed": "unknown"
            }
    
    async def _download_image_from_supabase(self, bucket: str, path: str) -> Optional[bytes]:
        """Download image from Supabase Storage"""
        try:
            # Use Supabase client to download
            from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
            
            # Construct storage URL
            storage_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
            
            headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
            }
            
            response = requests.get(storage_url, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Failed to download image: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
    
    async def _search_products_for_recommendations(
        self,
        recommendations: Dict[str, Any],
        user_skin_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Search for products based on AI recommendations"""
        
        if not self.search.is_enabled():
            logger.warning("Google Search is not enabled, using mock products")
            return {
                "products": [],
                "search_queries_used": [],
                "source": "mock"
            }
        
        all_products = []
        queries_used = []
        
        # Search based on conditions
        conditions = recommendations.get("conditions", [])
        if conditions:
            result = self.search.search_products_for_conditions(
                conditions=conditions[:3],  # Top 3 conditions
                user_profile=user_skin_profile
            )
            
            if result["success"]:
                all_products.extend(result["recommended_products"])
                queries_used.append(f"Conditions: {', '.join(conditions[:3])}")
        
        # Search for specific ingredients
        for ingredient in recommendations.get("recommended_ingredients", [])[:2]:
            query = f"skincare {ingredient} serum"
            result = self.search.search_products(query, max_results=5)
            
            if result["success"]:
                all_products.extend(result["products"])
                queries_used.append(query)
        
        # Deduplicate products
        seen_urls = set()
        unique_products = []
        for product in all_products:
            if product.get("url") and product["url"] not in seen_urls:
                seen_urls.add(product["url"])
                unique_products.append(product)
        
        # Sort by relevance
        unique_products.sort(key=lambda x: x.get("final_score", x.get("relevance_score", 0)), reverse=True)
        
        return {
            "products": unique_products[:10],  # Top 10 products
            "search_queries_used": queries_used,
            "total_found": len(unique_products),
            "source": "google_search"
        }
    
    def _generate_skincare_routine(
        self,
        analysis: Dict[str, Any],
        products: Dict[str, Any],
        user_skin_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate step-by-step skincare routine"""
        
        product_list = products.get("products", [])
        
        # Categorize products by type
        cleansers = [p for p in product_list if "cleanser" in p.get("name", "").lower()]
        serums = [p for p in product_list if "serum" in p.get("name", "").lower()]
        moisturizers = [p for p in product_list if "moisturizer" in p.get("name", "").lower() or "cream" in p.get("name", "").lower()]
        sunscreens = [p for p in product_list if "sunscreen" in p.get("name", "").lower() or "spf" in p.get("name", "").lower()]
        
        morning_routine = []
        evening_routine = []
        
        # Morning routine
        step = 1
        if cleansers:
            morning_routine.append({
                "step": step,
                "action": "Gentle Cleanser",
                "product": cleansers[0]["name"],
                "url": cleansers[0]["url"],
                "instructions": "Cleanse face with lukewarm water, massage for 60 seconds, rinse thoroughly"
            })
            step += 1
        
        if serums:
            for serum in serums[:2]:  # Up to 2 serums
                morning_routine.append({
                    "step": step,
                    "action": f"Treatment Serum",
                    "product": serum["name"],
                    "url": serum["url"],
                    "instructions": "Apply 2-3 drops, gently pat into skin, wait 1-2 minutes before next step"
                })
                step += 1
        
        if moisturizers:
            morning_routine.append({
                "step": step,
                "action": "Moisturizer",
                "product": moisturizers[0]["name"],
                "url": moisturizers[0]["url"],
                "instructions": "Apply while skin is slightly damp for better absorption"
            })
            step += 1
        
        if sunscreens:
            morning_routine.append({
                "step": step,
                "action": "Sunscreen SPF 30+",
                "product": sunscreens[0]["name"],
                "url": sunscreens[0]["url"],
                "instructions": "Apply generously, reapply every 2 hours if outdoors"
            })
        
        # Evening routine (similar but no sunscreen)
        step = 1
        if cleansers:
            evening_routine.append({
                "step": step,
                "action": "Double Cleanse",
                "product": cleansers[0]["name"],
                "url": cleansers[0]["url"],
                "instructions": "First with oil/balm, then with water-based cleanser"
            })
            step += 1
        
        if serums:
            for serum in serums[:2]:
                evening_routine.append({
                    "step": step,
                    "action": "Treatment Serum",
                    "product": serum["name"],
                    "url": serum["url"],
                    "instructions": "Apply on clean, dry skin"
                })
                step += 1
        
        if moisturizers:
            evening_routine.append({
                "step": step,
                "action": "Night Moisturizer",
                "product": moisturizers[0]["name"],
                "url": moisturizers[0]["url"],
                "instructions": "Apply generously as last step to seal in treatments"
            })
        
        return {
            "morning": morning_routine,
            "evening": evening_routine,
            "key_ingredients": analysis.get("recommended_ingredients", []),
            "timeline": "Expect to see improvements in 4-6 weeks with consistent use",
            "notes": [
                "Introduce new products one at a time (wait 1 week between additions)",
                "Always patch test new products",
                "Consistency is key - stick to routine for best results"
            ]
        }


# Global service instance
comprehensive_analysis_service = ComprehensiveSkinAnalysisService()

