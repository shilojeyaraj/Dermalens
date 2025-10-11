"""
OpenAI Vision API service for comprehensive skin analysis
"""
from openai import OpenAI
from typing import Dict, List, Optional, Any
import base64
import logging
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_ENABLED

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAISkinAnalysisService:
    """Service for analyzing skin conditions using OpenAI Vision API"""
    
    def __init__(self):
        """Initialize the OpenAI service"""
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL
        self.enabled = OPENAI_ENABLED and self.api_key
        self.client = None
        
        if self.enabled:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI Vision API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI API: {str(e)}")
                self.enabled = False
        else:
            logger.warning("OpenAI API is not enabled or missing API key")
    
    def is_enabled(self) -> bool:
        """Check if OpenAI API is enabled and configured"""
        return self.enabled
    
    def analyze_skin_image(
        self,
        image_data: bytes,
        user_profile: Optional[Dict[str, Any]] = None,
        user_skin_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze skin image using OpenAI Vision API
        
        Args:
            image_data: Raw image bytes
            user_profile: User's basic profile (email, username, etc.)
            user_skin_profile: User's detailed skin profile (allergies, concerns, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "OpenAI API is not enabled",
                "analysis": None
            }
        
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(user_profile, user_skin_profile)
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert dermatologist with years of experience in skin analysis and skincare recommendations."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            parsed_analysis = self._parse_analysis_response(analysis_text)
            
            return {
                "success": True,
                "analysis": parsed_analysis,
                "raw_response": analysis_text,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Error during OpenAI skin analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def _build_analysis_prompt(
        self,
        user_profile: Optional[Dict[str, Any]],
        user_skin_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Build comprehensive analysis prompt with user context"""
        
        prompt_parts = [
            "Please analyze this facial skin image comprehensively. Provide a detailed professional assessment including:",
            "",
            "1. **SKIN CONDITIONS DETECTED**",
            "   - List all visible skin conditions (acne, hyperpigmentation, wrinkles, redness, etc.)",
            "   - Rate severity for each condition (mild, moderate, severe)",
            "   - Identify specific areas affected",
            "",
            "2. **SKIN TYPE ASSESSMENT**",
            "   - Determine skin type (oily, dry, combination, normal)",
            "   - Assess hydration levels",
            "   - Note texture and pore visibility",
            "",
            "3. **ROOT CAUSES & FACTORS**",
            "   - Identify potential causes of detected issues",
            "   - Environmental factors to consider",
            "   - Lifestyle factors that may contribute",
            "",
            "4. **PERSONALIZED RECOMMENDATIONS**",
            "   - Specific ingredients to look for (e.g., niacinamide, retinol, hyaluronic acid)",
            "   - Product types needed (cleanser, serum, moisturizer, sunscreen)",
            "   - Treatment priorities (what to address first)",
            "   - Morning and evening routine suggestions",
            "",
            "5. **IMPROVEMENT TIMELINE**",
            "   - Expected timeline for visible improvements",
            "   - Milestones to track progress",
            "",
            "6. **PRECAUTIONS & WARNINGS**",
            "   - Ingredients or products to avoid",
            "   - Potential sensitivities to watch for",
            "   - When to seek professional help"
        ]
        
        # Add user-specific context
        if user_skin_profile:
            prompt_parts.extend([
                "",
                "**USER PROFILE CONTEXT:**"
            ])
            
            if user_skin_profile.get("skin_type"):
                prompt_parts.append(f"- User reports skin type as: {user_skin_profile['skin_type']}")
            
            if user_skin_profile.get("primary_concerns"):
                concerns = ", ".join(user_skin_profile["primary_concerns"])
                prompt_parts.append(f"- Main concerns: {concerns}")
            
            if user_skin_profile.get("allergies"):
                allergies = ", ".join(user_skin_profile["allergies"])
                prompt_parts.append(f"- **IMPORTANT - User is allergic to: {allergies}** (DO NOT recommend products with these ingredients)")
            
            if user_skin_profile.get("pre_existing_conditions"):
                conditions = ", ".join(user_skin_profile["pre_existing_conditions"])
                prompt_parts.append(f"- Pre-existing conditions: {conditions}")
            
            if user_skin_profile.get("sensitivity_level"):
                prompt_parts.append(f"- Sensitivity level: {user_skin_profile['sensitivity_level']}")
                if user_skin_profile["sensitivity_level"] == "high":
                    prompt_parts.append("  **Prioritize gentle, fragrance-free products**")
            
            if user_skin_profile.get("skin_goals"):
                goals = ", ".join(user_skin_profile["skin_goals"])
                prompt_parts.append(f"- Goals: {goals}")
        
        prompt_parts.extend([
            "",
            "Format your response in clear sections with markdown headings (##) for each category.",
            "Be specific, actionable, and personalized based on the image and user context provided."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parse OpenAI response into structured format"""
        
        # Initialize result structure
        result = {
            "conditions_detected": [],
            "skin_type": "unknown",
            "severity_assessment": {},
            "recommended_ingredients": [],
            "recommended_product_types": [],
            "routine_suggestions": {
                "morning": [],
                "evening": []
            },
            "precautions": [],
            "improvement_timeline": "",
            "full_analysis": analysis_text
        }
        
        # Extract conditions from text
        conditions_keywords = [
            "acne", "hyperpigmentation", "dark spots", "wrinkles", "fine lines",
            "rosacea", "eczema", "dryness", "oily", "blackheads", "whiteheads",
            "enlarged pores", "redness", "inflammation", "aging signs", "sun damage"
        ]
        
        analysis_lower = analysis_text.lower()
        for condition in conditions_keywords:
            if condition in analysis_lower:
                result["conditions_detected"].append(condition.replace(" ", "_"))
        
        # Extract skin type
        skin_types = ["oily", "dry", "combination", "normal", "sensitive"]
        for skin_type in skin_types:
            if skin_type in analysis_lower:
                result["skin_type"] = skin_type
                break
        
        # Extract recommended ingredients (common skincare actives)
        ingredients_keywords = [
            "niacinamide", "retinol", "hyaluronic acid", "vitamin c", "salicylic acid",
            "benzoyl peroxide", "azelaic acid", "glycolic acid", "ceramides",
            "peptides", "antioxidants", "spf", "sunscreen"
        ]
        
        for ingredient in ingredients_keywords:
            if ingredient in analysis_lower:
                result["recommended_ingredients"].append(ingredient)
        
        # Extract product types
        product_types = [
            "cleanser", "toner", "serum", "moisturizer", "sunscreen",
            "exfoliant", "mask", "spot treatment", "eye cream"
        ]
        
        for product_type in product_types:
            if product_type in analysis_lower:
                result["recommended_product_types"].append(product_type)
        
        return result
    
    def generate_personalized_recommendations(
        self,
        analysis_result: Dict[str, Any],
        user_skin_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate specific product and routine recommendations based on analysis
        
        Args:
            analysis_result: Results from analyze_skin_image
            user_skin_profile: User's skin profile for additional context
            
        Returns:
            Dictionary with personalized recommendations
        """
        if not analysis_result.get("success"):
            return {
                "success": False,
                "error": "Analysis failed, cannot generate recommendations"
            }
        
        analysis = analysis_result["analysis"]
        
        # Build product search queries based on detected conditions and recommendations
        search_queries = []
        
        # Add condition-specific searches
        for condition in analysis["conditions_detected"]:
            search_queries.append(f"treatment for {condition.replace('_', ' ')}")
        
        # Add ingredient-specific searches
        for ingredient in analysis["recommended_ingredients"][:3]:  # Top 3 ingredients
            search_queries.append(f"serum with {ingredient}")
        
        # Add product type searches
        for product_type in analysis["recommended_product_types"]:
            search_queries.append(f"{product_type} for {analysis['skin_type']} skin")
        
        return {
            "success": True,
            "search_queries": search_queries,
            "conditions": analysis["conditions_detected"],
            "recommended_ingredients": analysis["recommended_ingredients"],
            "recommended_products": analysis["recommended_product_types"],
            "skin_type": analysis["skin_type"],
            "full_analysis": analysis["full_analysis"]
        }


# Global service instance
openai_analysis_service = OpenAISkinAnalysisService()

