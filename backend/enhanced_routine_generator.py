#!/usr/bin/env python3
"""
Enhanced Skincare Routine Generator
Creates intelligent, personalized skincare routines using AI and ingredient science
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class EnhancedRoutineGenerator:
    """Advanced skincare routine generator with AI-powered personalization"""
    
    def __init__(self):
        self.routine_templates = self._load_routine_templates()
        self.ingredient_interactions = self._load_ingredient_interactions()
        self.skin_type_guidelines = self._load_skin_type_guidelines()
        self.condition_priorities = self._load_condition_priorities()
    
    def _load_routine_templates(self) -> Dict[str, Dict]:
        """Load base routine templates for different skin types and conditions"""
        return {
            "acne_prone": {
                "morning": ["gentle_cleanser", "niacinamide_serum", "lightweight_moisturizer", "sunscreen"],
                "evening": ["gentle_cleanser", "salicylic_acid_serum", "hydrating_moisturizer"],
                "weekly": ["clay_mask", "exfoliating_treatment"]
            },
            "anti_aging": {
                "morning": ["gentle_cleanser", "vitamin_c_serum", "peptide_moisturizer", "sunscreen"],
                "evening": ["gentle_cleanser", "retinol_serum", "rich_moisturizer"],
                "weekly": ["exfoliating_treatment", "hydrating_mask"]
            },
            "sensitive": {
                "morning": ["gentle_cleanser", "soothing_serum", "barrier_repair_moisturizer", "mineral_sunscreen"],
                "evening": ["gentle_cleanser", "calming_serum", "barrier_repair_moisturizer"],
                "weekly": ["soothing_mask"]
            },
            "hyperpigmentation": {
                "morning": ["gentle_cleanser", "vitamin_c_serum", "niacinamide_serum", "sunscreen"],
                "evening": ["gentle_cleanser", "arbutin_serum", "hydrating_moisturizer"],
                "weekly": ["exfoliating_treatment", "brightening_mask"]
            },
            "dry_skin": {
                "morning": ["gentle_cleanser", "hyaluronic_acid_serum", "rich_moisturizer", "sunscreen"],
                "evening": ["gentle_cleanser", "hydrating_serum", "night_cream"],
                "weekly": ["hydrating_mask", "facial_oil"]
            },
            "oily_skin": {
                "morning": ["foaming_cleanser", "niacinamide_serum", "oil_free_moisturizer", "sunscreen"],
                "evening": ["foaming_cleanser", "salicylic_acid_serum", "lightweight_moisturizer"],
                "weekly": ["clay_mask", "exfoliating_treatment"]
            }
        }
    
    def _load_ingredient_interactions(self) -> Dict[str, Dict]:
        """Load ingredient interaction data for safe routine building"""
        return {
            "vitamin_c": {
                "incompatible": ["retinol", "niacinamide"],
                "best_time": "morning",
                "ph_range": [3.0, 3.5],
                "wait_time": 15
            },
            "retinol": {
                "incompatible": ["vitamin_c", "acids", "benzoyl_peroxide"],
                "best_time": "evening",
                "ph_range": [5.0, 6.0],
                "wait_time": 30
            },
            "acids": {
                "incompatible": ["retinol", "vitamin_c"],
                "best_time": "evening",
                "ph_range": [3.0, 4.0],
                "wait_time": 20
            },
            "niacinamide": {
                "incompatible": ["vitamin_c"],
                "best_time": "morning_evening",
                "ph_range": [5.0, 7.0],
                "wait_time": 0
            }
        }
    
    def _load_skin_type_guidelines(self) -> Dict[str, Dict]:
        """Load specific guidelines for different skin types"""
        return {
            "dry": {
                "avoid": ["alcohol", "fragrance", "astringents", "clay"],
                "prefer": ["hyaluronic_acid", "ceramides", "glycerin", "oils"],
                "frequency": {"cleansing": 1, "moisturizing": 2, "exfoliating": 1}
            },
            "oily": {
                "avoid": ["heavy_oils", "comedogenic_ingredients"],
                "prefer": ["niacinamide", "salicylic_acid", "clay", "oil_free"],
                "frequency": {"cleansing": 2, "moisturizing": 1, "exfoliating": 2}
            },
            "combination": {
                "avoid": ["heavy_oils", "drying_ingredients"],
                "prefer": ["balanced_formulas", "niacinamide", "hyaluronic_acid"],
                "frequency": {"cleansing": 2, "moisturizing": 1, "exfoliating": 2}
            },
            "sensitive": {
                "avoid": ["fragrance", "alcohol", "acids", "retinol"],
                "prefer": ["soothing_ingredients", "ceramides", "gentle_formulas"],
                "frequency": {"cleansing": 1, "moisturizing": 1, "exfoliating": 0}
            },
            "normal": {
                "avoid": ["over_exfoliation"],
                "prefer": ["balanced_formulas", "antioxidants"],
                "frequency": {"cleansing": 2, "moisturizing": 1, "exfoliating": 1}
            }
        }
    
    def _load_condition_priorities(self) -> Dict[str, int]:
        """Load priority levels for different skin conditions"""
        return {
            "acne": 10,
            "severe_acne": 10,
            "rosacea": 9,
            "eczema": 9,
            "severe_hyperpigmentation": 8,
            "moderate_hyperpigmentation": 6,
            "mild_hyperpigmentation": 4,
            "severe_aging": 8,
            "moderate_aging": 6,
            "mild_aging": 4,
            "dry_skin": 5,
            "oily_skin": 5,
            "sensitive_skin": 7,
            "large_pores": 4,
            "dull_skin": 3
        }
    
    def generate_personalized_routine(
        self, 
        user_profile: Dict[str, Any], 
        analysis_results: List[Dict[str, Any]], 
        available_products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a comprehensive, personalized skincare routine"""
        try:
            # Extract user information
            skin_type = user_profile.get("skin_type", "normal").lower()
            concerns = user_profile.get("concerns", [])
            sensitivity_level = user_profile.get("sensitivity_level", "moderate")
            age = user_profile.get("age", 25)
            
            # Extract analysis data
            detected_conditions = []
            for result in analysis_results:
                detected_conditions.extend([c["condition"] for c in result.get("conditions", [])])
            
            # Determine primary concerns and create routine
            primary_concerns = self._prioritize_concerns(concerns + detected_conditions)
            routine_type = self._determine_routine_type(primary_concerns, skin_type, sensitivity_level)
            
            # Generate routine steps
            morning_routine = self._build_morning_routine(
                routine_type, skin_type, primary_concerns, available_products, age
            )
            evening_routine = self._build_evening_routine(
                routine_type, skin_type, primary_concerns, available_products, age
            )
            weekly_treatments = self._build_weekly_treatments(
                routine_type, skin_type, primary_concerns, available_products
            )
            
            # Add timing and frequency information
            routine = {
                "morning_routine": self._add_timing_info(morning_routine, "morning"),
                "evening_routine": self._add_timing_info(evening_routine, "evening"),
                "weekly_treatments": self._add_timing_info(weekly_treatments, "weekly"),
                "routine_type": routine_type,
                "targeted_concerns": primary_concerns,
                "estimated_duration": self._calculate_routine_duration(morning_routine, evening_routine),
                "difficulty_level": self._calculate_difficulty_level(morning_routine, evening_routine),
                "expected_results": self._predict_expected_results(primary_concerns, routine_type),
                "safety_notes": self._generate_safety_notes(skin_type, sensitivity_level, primary_concerns),
                "ingredient_conflicts": self._check_ingredient_conflicts(morning_routine + evening_routine),
                "created_at": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            return {
                "success": True,
                "routine": routine,
                "personalization_score": self._calculate_personalization_score(user_profile, routine),
                "effectiveness_prediction": self._predict_effectiveness(primary_concerns, routine_type)
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized routine: {e}")
            return {
                "success": False,
                "error": str(e),
                "routine": None
            }
    
    def _prioritize_concerns(self, concerns: List[str]) -> List[str]:
        """Prioritize concerns based on severity and impact"""
        # Score each concern
        concern_scores = []
        for concern in concerns:
            base_priority = self.condition_priorities.get(concern.lower(), 1)
            # Add modifiers for severity
            if "severe" in concern.lower():
                base_priority += 3
            elif "moderate" in concern.lower():
                base_priority += 1
            
            concern_scores.append((concern, base_priority))
        
        # Sort by priority (highest first)
        concern_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 5 concerns
        return [concern for concern, score in concern_scores[:5]]
    
    def _determine_routine_type(self, concerns: List[str], skin_type: str, sensitivity: str) -> str:
        """Determine the best routine type based on concerns and skin type"""
        if sensitivity == "high" or skin_type == "sensitive":
            return "sensitive"
        elif any(concern in ["acne", "severe_acne"] for concern in concerns):
            return "acne_prone"
        elif any(concern in ["hyperpigmentation", "dark_spots"] for concern in concerns):
            return "hyperpigmentation"
        elif any(concern in ["wrinkles", "aging"] for concern in concerns):
            return "anti_aging"
        elif skin_type == "dry":
            return "dry_skin"
        elif skin_type == "oily":
            return "oily_skin"
        else:
            return "normal"
    
    def _build_morning_routine(
        self, 
        routine_type: str, 
        skin_type: str, 
        concerns: List[str], 
        products: List[Dict], 
        age: int
    ) -> List[Dict[str, Any]]:
        """Build morning routine steps"""
        template = self.routine_templates.get(routine_type, self.routine_templates["normal"])
        morning_steps = template["morning"]
        
        routine_steps = []
        step_number = 1
        
        for step_type in morning_steps:
            # Find best product for this step
            product = self._find_best_product(step_type, skin_type, concerns, products, "morning")
            
            if product:
                routine_steps.append({
                    "step": step_number,
                    "action": self._get_action_name(step_type),
                    "product": product["name"],
                    "brand": product.get("brand", "Unknown"),
                    "category": step_type,
                    "ingredients": product.get("ingredients", ""),
                    "price": product.get("price", 0),
                    "rating": product.get("rating", 0),
                    "url": product.get("url", ""),
                    "instructions": self._get_step_instructions(step_type, skin_type, age),
                    "duration": self._get_step_duration(step_type),
                    "importance": self._get_step_importance(step_type, concerns),
                    "skin_type_suitability": self._check_skin_type_suitability(product, skin_type),
                    "concern_targeting": self._check_concern_targeting(product, concerns)
                })
                step_number += 1
        
        return routine_steps
    
    def _build_evening_routine(
        self, 
        routine_type: str, 
        skin_type: str, 
        concerns: List[str], 
        products: List[Dict], 
        age: int
    ) -> List[Dict[str, Any]]:
        """Build evening routine steps"""
        template = self.routine_templates.get(routine_type, self.routine_templates["normal"])
        evening_steps = template["evening"]
        
        routine_steps = []
        step_number = 1
        
        for step_type in evening_steps:
            product = self._find_best_product(step_type, skin_type, concerns, products, "evening")
            
            if product:
                routine_steps.append({
                    "step": step_number,
                    "action": self._get_action_name(step_type),
                    "product": product["name"],
                    "brand": product.get("brand", "Unknown"),
                    "category": step_type,
                    "ingredients": product.get("ingredients", ""),
                    "price": product.get("price", 0),
                    "rating": product.get("rating", 0),
                    "url": product.get("url", ""),
                    "instructions": self._get_step_instructions(step_type, skin_type, age),
                    "duration": self._get_step_duration(step_type),
                    "importance": self._get_step_importance(step_type, concerns),
                    "skin_type_suitability": self._check_skin_type_suitability(product, skin_type),
                    "concern_targeting": self._check_concern_targeting(product, concerns)
                })
                step_number += 1
        
        return routine_steps
    
    def _build_weekly_treatments(
        self, 
        routine_type: str, 
        skin_type: str, 
        concerns: List[str], 
        products: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Build weekly treatment steps"""
        template = self.routine_templates.get(routine_type, self.routine_templates["normal"])
        weekly_steps = template.get("weekly", [])
        
        routine_steps = []
        step_number = 1
        
        for step_type in weekly_steps:
            product = self._find_best_product(step_type, skin_type, concerns, products, "weekly")
            
            if product:
                routine_steps.append({
                    "step": step_number,
                    "action": self._get_action_name(step_type),
                    "product": product["name"],
                    "brand": product.get("brand", "Unknown"),
                    "category": step_type,
                    "ingredients": product.get("ingredients", ""),
                    "price": product.get("price", 0),
                    "rating": product.get("rating", 0),
                    "url": product.get("url", ""),
                    "instructions": self._get_step_instructions(step_type, skin_type, 25),
                    "duration": self._get_step_duration(step_type),
                    "frequency": self._get_weekly_frequency(step_type, skin_type),
                    "importance": self._get_step_importance(step_type, concerns),
                    "skin_type_suitability": self._check_skin_type_suitability(product, skin_type),
                    "concern_targeting": self._check_concern_targeting(product, concerns)
                })
                step_number += 1
        
        return routine_steps
    
    def _find_best_product(
        self, 
        step_type: str, 
        skin_type: str, 
        concerns: List[str], 
        products: List[Dict], 
        time_of_day: str
    ) -> Optional[Dict[str, Any]]:
        """Find the best product for a specific step"""
        if not products:
            return None
        
        # Filter products by category and skin type
        suitable_products = []
        for product in products:
            if self._is_product_suitable(product, step_type, skin_type, concerns, time_of_day):
                suitable_products.append(product)
        
        if not suitable_products:
            return None
        
        # Score products based on multiple factors
        scored_products = []
        for product in suitable_products:
            score = self._calculate_product_score(product, concerns, skin_type)
            scored_products.append((product, score))
        
        # Sort by score (highest first)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        return scored_products[0][0]
    
    def _is_product_suitable(
        self, 
        product: Dict[str, Any], 
        step_type: str, 
        skin_type: str, 
        concerns: List[str], 
        time_of_day: str
    ) -> bool:
        """Check if a product is suitable for the given criteria"""
        product_name = product.get("name", "").lower()
        product_type = product.get("product_type", "").lower()
        
        # Check category match
        if not self._matches_category(product_name, product_type, step_type):
            return False
        
        # Check skin type compatibility
        if not self._check_skin_type_compatibility(product, skin_type):
            return False
        
        # Check time of day compatibility
        if not self._check_time_compatibility(product, time_of_day):
            return False
        
        return True
    
    def _matches_category(self, product_name: str, product_type: str, step_type: str) -> bool:
        """Check if product matches the required category"""
        category_mapping = {
            "gentle_cleanser": ["cleanser", "wash", "foam"],
            "foaming_cleanser": ["foam", "cleanser"],
            "niacinamide_serum": ["niacinamide", "serum"],
            "vitamin_c_serum": ["vitamin c", "ascorbic", "serum"],
            "salicylic_acid_serum": ["salicylic", "serum"],
            "lightweight_moisturizer": ["moisturizer", "lotion", "gel"],
            "rich_moisturizer": ["moisturizer", "cream"],
            "sunscreen": ["sunscreen", "spf", "uv"],
            "clay_mask": ["clay", "mask"],
            "exfoliating_treatment": ["exfoliant", "acid", "scrub"]
        }
        
        keywords = category_mapping.get(step_type, [])
        return any(keyword in product_name or keyword in product_type for keyword in keywords)
    
    def _check_skin_type_compatibility(self, product: Dict[str, Any], skin_type: str) -> bool:
        """Check if product is compatible with skin type"""
        guidelines = self.skin_type_guidelines.get(skin_type, {})
        avoid_ingredients = guidelines.get("avoid", [])
        
        product_ingredients = product.get("ingredients", "").lower()
        product_name = product.get("name", "").lower()
        
        # Check if product contains ingredients to avoid
        for ingredient in avoid_ingredients:
            if ingredient in product_ingredients or ingredient in product_name:
                return False
        
        return True
    
    def _check_time_compatibility(self, product: Dict[str, Any], time_of_day: str) -> bool:
        """Check if product is suitable for the time of day"""
        product_ingredients = product.get("ingredients", "").lower()
        
        if time_of_day == "morning":
            # Avoid retinol and strong acids in morning
            if any(ingredient in product_ingredients for ingredient in ["retinol", "tretinoin"]):
                return False
        elif time_of_day == "evening":
            # Evening is more flexible
            return True
        elif time_of_day == "weekly":
            # Weekly treatments can be stronger
            return True
        
        return True
    
    def _calculate_product_score(self, product: Dict[str, Any], concerns: List[str], skin_type: str) -> float:
        """Calculate a score for product suitability"""
        score = 0.0
        
        # Base rating score
        rating = product.get("rating", 0)
        score += rating * 10
        
        # Price score (lower is better, but not too cheap)
        price = product.get("price", 0)
        if 10 <= price <= 50:
            score += 20
        elif 5 <= price <= 100:
            score += 10
        
        # Ingredient targeting score
        ingredients = product.get("ingredients", "").lower()
        for concern in concerns:
            if self._ingredient_targets_concern(ingredients, concern):
                score += 15
        
        # Skin type compatibility score
        if self._check_skin_type_compatibility(product, skin_type):
            score += 10
        
        return score
    
    def _ingredient_targets_concern(self, ingredients: str, concern: str) -> bool:
        """Check if ingredients target a specific concern"""
        concern_ingredients = {
            "acne": ["salicylic", "niacinamide", "benzoyl"],
            "hyperpigmentation": ["vitamin c", "arbutin", "glycolic"],
            "aging": ["retinol", "peptides", "vitamin c"],
            "dry_skin": ["hyaluronic", "glycerin", "ceramides"],
            "oily_skin": ["niacinamide", "salicylic", "clay"]
        }
        
        target_ingredients = concern_ingredients.get(concern.lower(), [])
        return any(ingredient in ingredients for ingredient in target_ingredients)
    
    def _get_action_name(self, step_type: str) -> str:
        """Get human-readable action name"""
        action_mapping = {
            "gentle_cleanser": "Gentle Cleanser",
            "foaming_cleanser": "Foaming Cleanser",
            "niacinamide_serum": "Niacinamide Treatment",
            "vitamin_c_serum": "Vitamin C Serum",
            "salicylic_acid_serum": "Salicylic Acid Treatment",
            "lightweight_moisturizer": "Lightweight Moisturizer",
            "rich_moisturizer": "Rich Moisturizer",
            "sunscreen": "Sunscreen",
            "clay_mask": "Clay Mask",
            "exfoliating_treatment": "Exfoliating Treatment"
        }
        return action_mapping.get(step_type, step_type.replace("_", " ").title())
    
    def _get_step_instructions(self, step_type: str, skin_type: str, age: int) -> str:
        """Get detailed instructions for each step"""
        instructions = {
            "gentle_cleanser": "Wet face with lukewarm water. Massage cleanser in circular motions for 60 seconds. Rinse thoroughly and pat dry.",
            "foaming_cleanser": "Wet face with lukewarm water. Work cleanser into a lather and massage for 60 seconds. Rinse thoroughly and pat dry.",
            "niacinamide_serum": "Apply 2-3 drops to clean skin. Gently pat and press into skin until absorbed. Wait 2-3 minutes before next step.",
            "vitamin_c_serum": "Apply 2-3 drops to clean skin in the morning. Gently pat into skin. Wait 15 minutes before applying sunscreen.",
            "salicylic_acid_serum": "Apply thin layer to affected areas. Start with every other night, then increase to nightly as tolerated.",
            "lightweight_moisturizer": "Apply evenly to face and neck while skin is slightly damp. Use gentle upward strokes.",
            "rich_moisturizer": "Apply generously to face and neck. Massage in upward circular motions until absorbed.",
            "sunscreen": "Apply liberally to face, neck, and ears. Reapply every 2 hours if outdoors. Use at least SPF 30.",
            "clay_mask": "Apply thin layer to clean skin. Leave on for 10-15 minutes. Rinse with lukewarm water.",
            "exfoliating_treatment": "Apply to clean, dry skin. Leave on for 5-10 minutes. Rinse thoroughly with lukewarm water."
        }
        
        base_instruction = instructions.get(step_type, "Follow product instructions.")
        
        # Add skin type specific advice
        if skin_type == "sensitive":
            base_instruction += " If irritation occurs, reduce frequency or discontinue use."
        elif skin_type == "oily":
            base_instruction += " Focus on T-zone area for oil control."
        elif skin_type == "dry":
            base_instruction += " Apply to slightly damp skin for better absorption."
        
        return base_instruction
    
    def _get_step_duration(self, step_type: str) -> str:
        """Get estimated duration for each step"""
        durations = {
            "gentle_cleanser": "1-2 minutes",
            "foaming_cleanser": "1-2 minutes",
            "niacinamide_serum": "30 seconds",
            "vitamin_c_serum": "1 minute",
            "salicylic_acid_serum": "30 seconds",
            "lightweight_moisturizer": "30 seconds",
            "rich_moisturizer": "1 minute",
            "sunscreen": "1 minute",
            "clay_mask": "10-15 minutes",
            "exfoliating_treatment": "5-10 minutes"
        }
        return durations.get(step_type, "1-2 minutes")
    
    def _get_weekly_frequency(self, step_type: str, skin_type: str) -> str:
        """Get recommended weekly frequency"""
        if skin_type == "sensitive":
            return "1-2 times per week"
        elif skin_type == "oily":
            return "2-3 times per week"
        else:
            return "1-2 times per week"
    
    def _get_step_importance(self, step_type: str, concerns: List[str]) -> str:
        """Get importance level for each step"""
        essential_steps = ["gentle_cleanser", "sunscreen"]
        important_steps = ["lightweight_moisturizer", "rich_moisturizer"]
        
        if step_type in essential_steps:
            return "Essential"
        elif step_type in important_steps:
            return "Important"
        else:
            return "Optional"
    
    def _check_skin_type_suitability(self, product: Dict[str, Any], skin_type: str) -> Dict[str, Any]:
        """Check how well product suits skin type"""
        guidelines = self.skin_type_guidelines.get(skin_type, {})
        avoid_ingredients = guidelines.get("avoid", [])
        prefer_ingredients = guidelines.get("prefer", [])
        
        product_ingredients = product.get("ingredients", "").lower()
        
        # Check for ingredients to avoid
        avoided_ingredients = [ingredient for ingredient in avoid_ingredients if ingredient in product_ingredients]
        
        # Check for preferred ingredients
        preferred_ingredients = [ingredient for ingredient in prefer_ingredients if ingredient in product_ingredients]
        
        # Calculate suitability score
        score = 100
        score -= len(avoided_ingredients) * 20
        score += len(preferred_ingredients) * 10
        
        return {
            "score": max(0, min(100, score)),
            "avoided_ingredients": avoided_ingredients,
            "preferred_ingredients": preferred_ingredients,
            "suitability": "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"
        }
    
    def _check_concern_targeting(self, product: Dict[str, Any], concerns: List[str]) -> Dict[str, Any]:
        """Check how well product targets specific concerns"""
        product_ingredients = product.get("ingredients", "").lower()
        targeted_concerns = []
        
        for concern in concerns:
            if self._ingredient_targets_concern(product_ingredients, concern):
                targeted_concerns.append(concern)
        
        targeting_score = (len(targeted_concerns) / len(concerns)) * 100 if concerns else 0
        
        return {
            "targeted_concerns": targeted_concerns,
            "targeting_score": targeting_score,
            "effectiveness": "High" if targeting_score >= 70 else "Medium" if targeting_score >= 40 else "Low"
        }
    
    def _add_timing_info(self, routine_steps: List[Dict], time_of_day: str) -> List[Dict[str, Any]]:
        """Add timing and scheduling information to routine steps"""
        for i, step in enumerate(routine_steps):
            step["time_of_day"] = time_of_day
            step["estimated_start_time"] = self._calculate_start_time(time_of_day, i)
            step["wait_time_after"] = self._get_wait_time_after(step.get("category", ""))
        
        return routine_steps
    
    def _calculate_start_time(self, time_of_day: str, step_index: int) -> str:
        """Calculate estimated start time for each step"""
        if time_of_day == "morning":
            base_time = "7:00 AM"
        elif time_of_day == "evening":
            base_time = "9:00 PM"
        else:  # weekly
            base_time = "8:00 PM"
        
        # Add 5 minutes for each previous step
        minutes_to_add = step_index * 5
        return f"{base_time} +{minutes_to_add}min"
    
    def _get_wait_time_after(self, category: str) -> str:
        """Get recommended wait time after applying product"""
        wait_times = {
            "vitamin_c_serum": "15 minutes",
            "retinol_serum": "30 minutes",
            "salicylic_acid_serum": "20 minutes",
            "niacinamide_serum": "2-3 minutes",
            "lightweight_moisturizer": "1-2 minutes",
            "rich_moisturizer": "2-3 minutes"
        }
        return wait_times.get(category, "1-2 minutes")
    
    def _calculate_routine_duration(self, morning_routine: List[Dict], evening_routine: List[Dict]) -> str:
        """Calculate total estimated routine duration"""
        morning_duration = len(morning_routine) * 2  # 2 minutes per step
        evening_duration = len(evening_routine) * 2
        total_minutes = morning_duration + evening_duration
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}min"
    
    def _calculate_difficulty_level(self, morning_routine: List[Dict], evening_routine: List[Dict]) -> str:
        """Calculate routine difficulty level"""
        total_steps = len(morning_routine) + len(evening_routine)
        
        if total_steps <= 4:
            return "Beginner"
        elif total_steps <= 6:
            return "Intermediate"
        else:
            return "Advanced"
    
    def _predict_expected_results(self, concerns: List[str], routine_type: str) -> List[str]:
        """Predict expected results from the routine"""
        results = []
        
        if "acne" in " ".join(concerns).lower():
            results.append("Reduced acne breakouts and inflammation")
            results.append("Clearer, smoother skin texture")
        
        if "hyperpigmentation" in " ".join(concerns).lower() or "dark_spots" in " ".join(concerns).lower():
            results.append("Faded dark spots and hyperpigmentation")
            results.append("More even skin tone")
        
        if "aging" in " ".join(concerns).lower() or "wrinkles" in " ".join(concerns).lower():
            results.append("Reduced fine lines and wrinkles")
            results.append("Firmer, more youthful-looking skin")
        
        if "dry_skin" in " ".join(concerns).lower():
            results.append("Improved skin hydration and moisture retention")
            results.append("Smoother, more supple skin")
        
        if "oily_skin" in " ".join(concerns).lower():
            results.append("Better oil control and reduced shine")
            results.append("Minimized pore appearance")
        
        # Add general results
        results.extend([
            "Overall improved skin health and appearance",
            "Better skin texture and radiance"
        ])
        
        return results[:5]  # Limit to 5 results
    
    def _generate_safety_notes(self, skin_type: str, sensitivity: str, concerns: List[str]) -> List[str]:
        """Generate safety notes for the routine"""
        notes = []
        
        if sensitivity == "high" or skin_type == "sensitive":
            notes.append("Start with lower concentrations and patch test all products")
            notes.append("If irritation occurs, reduce frequency or discontinue use")
        
        if "acne" in " ".join(concerns).lower():
            notes.append("Introduce acne treatments gradually to avoid purging")
            notes.append("Always use sunscreen when using acne treatments")
        
        if "retinol" in " ".join(concerns).lower():
            notes.append("Start retinol slowly - every other night initially")
            notes.append("Never use retinol with vitamin C or acids")
            notes.append("Always use sunscreen when using retinol")
        
        notes.append("Always patch test new products before full application")
        notes.append("Consult a dermatologist if you experience persistent irritation")
        
        return notes
    
    def _check_ingredient_conflicts(self, routine_steps: List[Dict]) -> List[Dict[str, Any]]:
        """Check for ingredient conflicts in the routine"""
        conflicts = []
        all_ingredients = []
        
        # Collect all ingredients
        for step in routine_steps:
            ingredients = step.get("ingredients", "").lower()
            all_ingredients.extend(ingredients.split(", "))
        
        # Check for known conflicts
        for ingredient in all_ingredients:
            interactions = self.ingredient_interactions.get(ingredient, {})
            incompatible = interactions.get("incompatible", [])
            
            for other_ingredient in all_ingredients:
                if other_ingredient != ingredient and other_ingredient in incompatible:
                    conflicts.append({
                        "ingredient_1": ingredient,
                        "ingredient_2": other_ingredient,
                        "conflict_type": "incompatible",
                        "recommendation": "Use on alternate days or different times"
                    })
        
        return conflicts
    
    def _calculate_personalization_score(self, user_profile: Dict[str, Any], routine: Dict[str, Any]) -> int:
        """Calculate how well the routine is personalized for the user"""
        score = 0
        
        # Base score
        score += 20
        
        # Skin type matching
        skin_type = user_profile.get("skin_type", "normal")
        if routine.get("routine_type") == skin_type:
            score += 20
        
        # Concern targeting
        concerns = user_profile.get("concerns", [])
        targeted_concerns = routine.get("targeted_concerns", [])
        if concerns:
            targeting_ratio = len(set(concerns) & set(targeted_concerns)) / len(concerns)
            score += int(targeting_ratio * 30)
        
        # Age appropriateness
        age = user_profile.get("age", 25)
        if age > 30 and "anti_aging" in routine.get("routine_type", ""):
            score += 15
        elif age < 25 and "anti_aging" not in routine.get("routine_type", ""):
            score += 15
        
        # Sensitivity consideration
        sensitivity = user_profile.get("sensitivity_level", "moderate")
        if sensitivity == "high" and "sensitive" in routine.get("routine_type", ""):
            score += 15
        
        return min(100, score)
    
    def _predict_effectiveness(self, concerns: List[str], routine_type: str) -> Dict[str, Any]:
        """Predict the effectiveness of the routine"""
        effectiveness_scores = {
            "acne_prone": 85,
            "anti_aging": 80,
            "hyperpigmentation": 75,
            "sensitive": 70,
            "dry_skin": 80,
            "oily_skin": 85,
            "normal": 75
        }
        
        base_score = effectiveness_scores.get(routine_type, 70)
        
        # Adjust based on number of concerns
        concern_count = len(concerns)
        if concern_count == 1:
            base_score += 10
        elif concern_count >= 3:
            base_score -= 10
        
        return {
            "overall_effectiveness": base_score,
            "expected_improvement_time": "4-8 weeks",
            "confidence_level": "High" if base_score >= 80 else "Medium" if base_score >= 70 else "Low"
        }

# Create global instance
enhanced_routine_generator = EnhancedRoutineGenerator()

