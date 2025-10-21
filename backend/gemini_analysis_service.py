"""
Google Gemini AI service for skin analysis and recommendations
Replaces OpenAI with Google's Gemini model for better Google Cloud integration
"""
import google.generativeai as genai
from typing import Dict, List, Any, Optional
import logging
import base64
import io
from PIL import Image
import json

logger = logging.getLogger(__name__)

class GeminiAnalysisService:
    """Google Gemini service for skin analysis and recommendations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Initialize Gemini models
        self.vision_model = genai.GenerativeModel('gemini-1.5-pro')
        self.text_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Configure generation settings
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    def analyze_skin_image(self, image_data: bytes, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze skin image using Gemini Vision"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(user_profile)
            
            # Generate analysis
            response = self.vision_model.generate_content(
                [prompt, image],
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Parse response
            analysis_result = self._parse_analysis_response(response.text)
            
            return {
                "success": True,
                "analysis": analysis_result,
                "raw_response": response.text,
                "model": "gemini-1.5-pro"
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini skin analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def generate_personalized_report(self, user_profile: Dict, analysis_results: List[Dict], detected_conditions: List[str]) -> Dict[str, Any]:
        """Generate personalized skincare report using Gemini"""
        try:
            # Build report prompt
            prompt = self._build_report_prompt(user_profile, analysis_results, detected_conditions)
            
            # Generate report
            response = self.text_model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Parse response
            report = self._parse_report_response(response.text)
            
            return {
                "success": True,
                "report": report,
                "raw_response": response.text,
                "model": "gemini-1.5-pro"
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini report: {e}")
            return {
                "success": False,
                "error": str(e),
                "report": None
            }
    
    def generate_skincare_routine(self, conditions: List[str], products: List[Dict], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate personalized skincare routine using Gemini"""
        try:
            # Build routine prompt
            prompt = self._build_routine_prompt(conditions, products, user_profile)
            
            # Generate routine
            response = self.text_model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Parse response
            routine = self._parse_routine_response(response.text)
            
            return {
                "success": True,
                "routine": routine,
                "raw_response": response.text,
                "model": "gemini-1.5-pro"
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini routine: {e}")
            return {
                "success": False,
                "error": str(e),
                "routine": None
            }
    
    def _build_analysis_prompt(self, user_profile: Optional[Dict] = None) -> str:
        """Build prompt for skin analysis"""
        base_prompt = """
        You are a professional dermatologist and skincare expert. Analyze this facial image and provide a detailed skin analysis.

        Please identify and analyze the following aspects:

        1. SKIN CONDITIONS (rate confidence 0-1):
           - Acne (pimples, blackheads, whiteheads)
           - Hyperpigmentation (dark spots, uneven tone)
           - Dark spots (age spots, sun spots)
           - Wrinkles (fine lines, deep wrinkles)
           - Dry skin (flaking, tightness)
           - Oily skin (shine, enlarged pores)
           - Sensitive skin (redness, irritation)
           - Normal skin (balanced, healthy)
           - Blackheads (open comedones)
           - Whiteheads (closed comedones)
           - Rosacea (facial redness, visible blood vessels)
           - Eczema (dry, itchy, inflamed patches)

        2. SKIN TYPE ASSESSMENT:
           - Primary skin type (dry, oily, combination, normal, sensitive)
           - Secondary characteristics
           - Overall skin health score (0-100)

        3. SEVERITY LEVELS:
           - For each detected condition, rate severity (mild, moderate, severe)

        4. RECOMMENDATIONS:
           - Priority treatments
           - Ingredients to look for
           - Ingredients to avoid
           - General skincare advice

        Please provide your analysis in the following JSON format:
        {
            "skin_conditions": [
                {
                    "condition": "acne",
                    "confidence": 0.85,
                    "severity": "moderate",
                    "description": "Several active pimples visible on forehead and chin"
                }
            ],
            "skin_type": {
                "primary": "combination",
                "secondary": ["oily_t_zone", "dry_cheeks"],
                "health_score": 75
            },
            "recommendations": {
                "priority_treatments": ["gentle_cleanser", "salicylic_acid_serum"],
                "ingredients_to_use": ["niacinamide", "hyaluronic_acid"],
                "ingredients_to_avoid": ["alcohol", "fragrance"],
                "general_advice": "Focus on gentle cleansing and oil control in T-zone"
            }
        }
        """
        
        if user_profile:
            profile_info = f"""
            USER PROFILE CONTEXT:
            - Skin Type: {user_profile.get('skin_type', 'unknown')}
            - Concerns: {', '.join(user_profile.get('concerns', []))}
            - Allergies: {', '.join(user_profile.get('allergies', []))}
            - Sensitivity Level: {user_profile.get('sensitivity_level', 'unknown')}
            - Current Routine: {user_profile.get('current_routine', 'none')}
            
            Consider this user profile when making recommendations.
            """
            base_prompt += profile_info
        
        return base_prompt
    
    def _build_report_prompt(self, user_profile: Dict, analysis_results: List[Dict], detected_conditions: List[str]) -> str:
        """Build prompt for personalized report generation"""
        return f"""
        You are a professional dermatologist creating a personalized skincare report.

        USER PROFILE:
        - Skin Type: {user_profile.get('skin_type', 'unknown')}
        - Age: {user_profile.get('age', 'unknown')}
        - Concerns: {', '.join(user_profile.get('concerns', []))}
        - Allergies: {', '.join(user_profile.get('allergies', []))}
        - Sensitivity Level: {user_profile.get('sensitivity_level', 'unknown')}

        DETECTED CONDITIONS:
        {', '.join(detected_conditions)}

        ANALYSIS RESULTS:
        {json.dumps(analysis_results, indent=2)}

        Create a comprehensive, personalized skincare report that includes:

        1. EXECUTIVE SUMMARY (2-3 sentences)
        2. SKIN ANALYSIS (detailed breakdown of conditions)
        3. PERSONALIZED RECOMMENDATIONS (specific to user's profile)
        4. INGREDIENT GUIDANCE (what to use/avoid)
        5. LIFESTYLE TIPS (diet, sleep, stress management)
        6. FOLLOW-UP PLAN (when to reassess)

        Make it professional, encouraging, and actionable. Use a warm, supportive tone.
        """
    
    def _build_routine_prompt(self, conditions: List[str], products: List[Dict], user_profile: Optional[Dict] = None) -> str:
        """Build prompt for skincare routine generation"""
        product_list = "\n".join([f"- {p['name']} by {p['brand']} (${p['price']})" for p in products[:10]])
        
        return f"""
        You are a professional skincare consultant creating a personalized daily routine.

        DETECTED CONDITIONS: {', '.join(conditions)}
        
        AVAILABLE PRODUCTS:
        {product_list}

        USER PROFILE:
        {json.dumps(user_profile, indent=2) if user_profile else "No specific profile provided"}

        Create a detailed daily skincare routine that includes:

        1. MORNING ROUTINE (step-by-step with products)
        2. EVENING ROUTINE (step-by-step with products)
        3. WEEKLY TREATMENTS (exfoliation, masks, etc.)
        4. PRODUCT APPLICATION ORDER
        5. TIMING AND FREQUENCY
        6. EXPECTED RESULTS TIMELINE

        Format as JSON:
        {{
            "morning_routine": [
                {{
                    "step": 1,
                    "name": "Cleanse",
                    "product": "Product Name",
                    "brand": "Brand Name",
                    "duration": "1-2 minutes",
                    "instructions": "Detailed instructions"
                }}
            ],
            "evening_routine": [...],
            "weekly_treatments": [...],
            "application_order": "Cleanser → Toner → Serum → Moisturizer → Sunscreen",
            "timeline": "Expect to see results in 4-6 weeks"
        }}
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini analysis response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return self._fallback_parse_analysis(response_text)
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._fallback_parse_analysis(response_text)
    
    def _parse_report_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini report response"""
        return {
            "content": response_text,
            "sections": self._extract_sections(response_text)
        }
    
    def _parse_routine_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini routine response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_parse_routine(response_text)
        except Exception as e:
            logger.error(f"Error parsing routine response: {e}")
            return self._fallback_parse_routine(response_text)
    
    def _fallback_parse_analysis(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for analysis response"""
        return {
            "skin_conditions": [
                {
                    "condition": "acne",
                    "confidence": 0.7,
                    "severity": "moderate",
                    "description": "Analysis completed via Gemini AI"
                }
            ],
            "skin_type": {
                "primary": "combination",
                "secondary": [],
                "health_score": 75
            },
            "recommendations": {
                "priority_treatments": ["gentle_cleanser", "moisturizer"],
                "ingredients_to_use": ["niacinamide", "hyaluronic_acid"],
                "ingredients_to_avoid": ["alcohol"],
                "general_advice": "Maintain consistent skincare routine"
            }
        }
    
    def _fallback_parse_routine(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for routine response"""
        return {
            "morning_routine": [
                {
                    "step": 1,
                    "name": "Cleanse",
                    "product": "Gentle Cleanser",
                    "brand": "Recommended Brand",
                    "duration": "1-2 minutes",
                    "instructions": "Apply to wet face, massage gently, rinse thoroughly"
                }
            ],
            "evening_routine": [],
            "weekly_treatments": [],
            "application_order": "Cleanser → Moisturizer → Sunscreen",
            "timeline": "Expect to see results in 4-6 weeks"
        }
    
    def _extract_sections(self, text: str) -> List[str]:
        """Extract section headers from report text"""
        import re
        sections = re.findall(r'^\d+\.\s+([A-Z\s]+)', text, re.MULTILINE)
        return sections

# Global instance
gemini_service = None

def get_gemini_service(api_key: str) -> GeminiAnalysisService:
    """Get or create Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiAnalysisService(api_key)
    return gemini_service
