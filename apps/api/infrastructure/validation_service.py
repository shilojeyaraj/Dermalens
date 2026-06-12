#!/usr/bin/env python3
"""
Validation Service for Skincare Recommendations
Ensures skincare routines are safe, effective, and personalized
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SkincareValidationService:
    """Service for validating skincare recommendations and routines"""

    def __init__(self):
        self.skin_conditions = [
            "acne",
            "blackheads",
            "whiteheads",
            "dark_spots",
            "hyperpigmentation",
            "wrinkles",
            "dry_skin",
            "oily_skin",
            "sensitive_skin",
            "normal_skin",
            "rosacea",
            "eczema",
            "large_pores",
            "uneven_texture",
            "dull_skin",
        ]
        self.skin_types = ["dry", "oily", "combination", "normal", "sensitive"]
        self.product_types = [
            "cleanser",
            "serum",
            "moisturizer",
            "sunscreen",
            "exfoliant",
            "toner",
            "mask",
        ]

        # Safety guidelines
        self.safety_guidelines = {
            "acids": {
                "max_daily": 1,
                "concentration_limits": {
                    "salicylic_acid": 2.0,
                    "glycolic_acid": 10.0,
                    "lactic_acid": 10.0,
                },
                "incompatible": ["retinol", "vitamin_c"],
                "warnings": ["sensitive_skin", "pregnancy"],
            },
            "retinol": {
                "max_daily": 1,
                "concentration_limits": {"retinol": 1.0},
                "incompatible": ["vitamin_c", "acids"],
                "warnings": ["sensitive_skin", "pregnancy", "sun_exposure"],
            },
            "vitamin_c": {
                "max_daily": 1,
                "concentration_limits": {"vitamin_c": 20.0},
                "incompatible": ["retinol", "niacinamide"],
                "warnings": ["sensitive_skin"],
            },
        }

    def validate_skincare_routine(
        self, routine: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a complete skincare routine for safety and effectiveness"""
        try:
            validation_results = {
                "is_valid": True,
                "warnings": [],
                "errors": [],
                "recommendations": [],
                "safety_score": 100,
                "effectiveness_score": 0,
            }

            # Extract routine components
            morning_routine = routine.get("morning_routine", [])
            evening_routine = routine.get("evening_routine", [])

            # Validate each routine
            morning_validation = self._validate_routine_steps(
                morning_routine, "morning", user_profile
            )
            evening_validation = self._validate_routine_steps(
                evening_routine, "evening", user_profile
            )

            # Combine results
            validation_results["warnings"].extend(morning_validation["warnings"])
            validation_results["warnings"].extend(evening_validation["warnings"])
            validation_results["errors"].extend(morning_validation["errors"])
            validation_results["errors"].extend(evening_validation["errors"])
            validation_results["recommendations"].extend(morning_validation["recommendations"])
            validation_results["recommendations"].extend(evening_validation["recommendations"])

            # Calculate safety score
            validation_results["safety_score"] = self._calculate_safety_score(
                morning_validation, evening_validation
            )

            # Calculate effectiveness score
            validation_results["effectiveness_score"] = self._calculate_effectiveness_score(
                routine, user_profile
            )

            # Overall validation
            validation_results["is_valid"] = len(validation_results["errors"]) == 0

            return validation_results

        except Exception as e:
            logger.error(f"Error validating skincare routine: {e}")
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "safety_score": 0,
                "effectiveness_score": 0,
            }

    def _validate_routine_steps(
        self, steps: List[Dict], routine_type: str, user_profile: Dict
    ) -> Dict[str, Any]:
        """Validate individual routine steps"""
        validation = {"warnings": [], "errors": [], "recommendations": []}

        # Check for essential steps
        step_types = [step.get("action", "").lower() for step in steps]

        if routine_type == "morning":
            if "sunscreen" not in " ".join(step_types):
                validation["warnings"].append("Morning routine should include sunscreen")
                validation["recommendations"].append("Add SPF 30+ sunscreen as the last step")

        # Merge results from each sub-validator. Each returns its own
        # warnings/errors/recommendations lists, so we EXTEND (not dict.update,
        # which would overwrite and silently drop the checks accumulated above).
        sub_validations = (
            self._validate_step_order(steps, routine_type),
            self._validate_ingredient_conflicts(steps, user_profile),
            self._validate_skin_type_compatibility(steps, user_profile),
            self._validate_condition_targeting(steps, user_profile),
        )
        for sub in sub_validations:
            for key in ("warnings", "errors", "recommendations"):
                validation[key].extend(sub.get(key, []))

        return validation

    def _validate_step_order(self, steps: List[Dict], routine_type: str) -> Dict[str, Any]:
        """Validate that steps are in the correct order"""
        validation = {"warnings": [], "errors": [], "recommendations": []}

        # Expected order for morning routine
        morning_order = ["cleanser", "toner", "serum", "moisturizer", "sunscreen"]
        evening_order = ["cleanser", "toner", "serum", "moisturizer"]

        expected_order = morning_order if routine_type == "morning" else evening_order

        # Check if steps follow expected order
        current_order = []
        for step in steps:
            action = step.get("action", "").lower()
            if any(keyword in action for keyword in expected_order):
                current_order.append(action)

        # Validate order
        for i, step in enumerate(current_order):
            if i < len(expected_order):
                expected = expected_order[i]
                if expected not in step and i > 0:
                    validation["warnings"].append(f"Step order may not be optimal: {step}")
                    validation["recommendations"].append(
                        f"Consider following the order: {', '.join(expected_order)}"
                    )

        return validation

    def _validate_ingredient_conflicts(
        self, steps: List[Dict], user_profile: Dict
    ) -> Dict[str, Any]:
        """Validate for ingredient conflicts and interactions"""
        validation = {"warnings": [], "errors": [], "recommendations": []}

        # Extract all ingredients from steps
        all_ingredients = []
        for step in steps:
            product = step.get("product", "")
            ingredients = self._extract_ingredients_from_product(product)
            all_ingredients.extend(ingredients)

        # Check for conflicts
        for ingredient in all_ingredients:
            ingredient_lower = ingredient.lower()

            # Check acid conflicts
            if any(acid in ingredient_lower for acid in ["salicylic", "glycolic", "lactic"]):
                if any(
                    conflict in " ".join(all_ingredients).lower()
                    for conflict in ["retinol", "vitamin c"]
                ):
                    validation["warnings"].append(
                        f"{ingredient} may conflict with other active ingredients"
                    )
                    validation["recommendations"].append(
                        "Use acids and other actives on alternate nights"
                    )

            # Check retinol conflicts
            if "retinol" in ingredient_lower:
                if any(
                    conflict in " ".join(all_ingredients).lower()
                    for conflict in ["vitamin c", "acid"]
                ):
                    validation["warnings"].append("Retinol may conflict with vitamin C or acids")
                    validation["recommendations"].append(
                        "Use retinol on alternate nights from other actives"
                    )

            # Check vitamin C conflicts
            if "vitamin c" in ingredient_lower or "ascorbic" in ingredient_lower:
                if any(
                    conflict in " ".join(all_ingredients).lower()
                    for conflict in ["retinol", "niacinamide"]
                ):
                    validation["warnings"].append(
                        "Vitamin C may conflict with retinol or niacinamide"
                    )
                    validation["recommendations"].append(
                        "Use vitamin C in the morning, other actives at night"
                    )

        return validation

    def _validate_skin_type_compatibility(
        self, steps: List[Dict], user_profile: Dict
    ) -> Dict[str, Any]:
        """Validate that products are compatible with user's skin type"""
        validation = {"warnings": [], "errors": [], "recommendations": []}

        skin_type = user_profile.get("skin_type", "normal").lower()

        for step in steps:
            product = step.get("product", "").lower()
            action = step.get("action", "").lower()

            # Check for skin type incompatibilities
            if skin_type == "sensitive":
                if any(ingredient in product for ingredient in ["acid", "retinol", "vitamin c"]):
                    validation["warnings"].append(f"{product} may be too strong for sensitive skin")
                    validation["recommendations"].append(
                        "Consider gentler alternatives for sensitive skin"
                    )

            elif skin_type == "oily":
                if "oil" in product and "cleanser" not in action:
                    validation["warnings"].append(f"{product} may be too heavy for oily skin")
                    validation["recommendations"].append(
                        "Consider oil-free or lightweight alternatives"
                    )

            elif skin_type == "dry":
                if any(ingredient in product for ingredient in ["clay", "alcohol", "astringent"]):
                    validation["warnings"].append(f"{product} may be too drying for dry skin")
                    validation["recommendations"].append("Consider more hydrating alternatives")

        return validation

    def _validate_condition_targeting(
        self, steps: List[Dict], user_profile: Dict
    ) -> Dict[str, Any]:
        """Validate that routine targets user's skin conditions"""
        validation = {"warnings": [], "recommendations": []}

        conditions = user_profile.get("concerns", [])
        all_products = " ".join([step.get("product", "") for step in steps]).lower()

        # Check if routine addresses specific conditions
        condition_ingredients = {
            "acne": ["salicylic", "niacinamide", "benzoyl"],
            "dark_spots": ["vitamin c", "arbutin", "glycolic"],
            "wrinkles": ["retinol", "peptides", "vitamin c"],
            "dry_skin": ["hyaluronic", "glycerin", "ceramides"],
            "oily_skin": ["niacinamide", "salicylic", "clay"],
        }

        for condition in conditions:
            condition_lower = condition.lower()
            if condition_lower in condition_ingredients:
                target_ingredients = condition_ingredients[condition_lower]
                if not any(ingredient in all_products for ingredient in target_ingredients):
                    validation["recommendations"].append(
                        f"Consider adding ingredients to target {condition}: {', '.join(target_ingredients)}"
                    )

        return validation

    def _extract_ingredients_from_product(self, product_name: str) -> List[str]:
        """Extract ingredient names from product name"""
        # Simple extraction - in real implementation, this would query a product database
        ingredients = []
        product_lower = product_name.lower()

        ingredient_keywords = [
            "salicylic",
            "glycolic",
            "lactic",
            "vitamin c",
            "retinol",
            "niacinamide",
            "hyaluronic",
            "glycerin",
            "ceramides",
            "peptides",
            "aloe",
            "centella",
        ]

        for keyword in ingredient_keywords:
            if keyword in product_lower:
                ingredients.append(keyword)

        return ingredients

    def _calculate_safety_score(self, morning_validation: Dict, evening_validation: Dict) -> int:
        """Calculate safety score based on validation results"""
        score = 100

        # Deduct points for warnings and errors
        score -= len(morning_validation["warnings"]) * 5
        score -= len(morning_validation["errors"]) * 15
        score -= len(evening_validation["warnings"]) * 5
        score -= len(evening_validation["errors"]) * 15

        return max(0, score)

    def _calculate_effectiveness_score(self, routine: Dict, user_profile: Dict) -> int:
        """Calculate effectiveness score based on routine completeness and targeting"""
        score = 0

        # Base score for having a routine
        score += 20

        # Check for essential steps
        morning_steps = routine.get("morning_routine", [])
        evening_steps = routine.get("evening_routine", [])

        if any("cleanser" in step.get("action", "").lower() for step in morning_steps):
            score += 15
        if any("sunscreen" in step.get("action", "").lower() for step in morning_steps):
            score += 20
        if any(
            "moisturizer" in step.get("action", "").lower()
            for step in morning_steps + evening_steps
        ):
            score += 15

        # Check for condition targeting
        conditions = user_profile.get("concerns", [])
        all_products = " ".join(
            [step.get("product", "") for step in morning_steps + evening_steps]
        ).lower()

        condition_ingredients = {
            "acne": ["salicylic", "niacinamide"],
            "dark_spots": ["vitamin c", "glycolic"],
            "wrinkles": ["retinol", "peptides"],
            "dry_skin": ["hyaluronic", "glycerin"],
            "oily_skin": ["niacinamide", "salicylic"],
        }

        targeted_conditions = 0
        for condition in conditions:
            condition_lower = condition.lower()
            if condition_lower in condition_ingredients:
                if any(
                    ingredient in all_products
                    for ingredient in condition_ingredients[condition_lower]
                ):
                    targeted_conditions += 1

        if conditions:
            score += (targeted_conditions / len(conditions)) * 30

        return min(100, score)

    def validate_product_recommendation(
        self, product: Dict[str, Any], user_profile: Dict
    ) -> Dict[str, Any]:
        """Validate a single product recommendation"""
        validation = {
            "is_suitable": True,
            "warnings": [],
            "recommendations": [],
            "suitability_score": 100,
        }

        skin_type = user_profile.get("skin_type", "normal").lower()
        conditions = user_profile.get("concerns", [])

        # Check skin type compatibility
        product_name = product.get("name", "").lower()
        product_ingredients = product.get("ingredients", "").lower()

        if skin_type == "sensitive":
            if any(
                ingredient in product_ingredients
                for ingredient in ["alcohol", "fragrance", "parabens"]
            ):
                validation["warnings"].append("Product may contain irritants for sensitive skin")
                validation["suitability_score"] -= 20

        elif skin_type == "oily":
            if "oil" in product_name and "cleanser" not in product_name:
                validation["warnings"].append("Oil-based product may be too heavy for oily skin")
                validation["suitability_score"] -= 15

        elif skin_type == "dry":
            if any(
                ingredient in product_ingredients
                for ingredient in ["clay", "alcohol", "astringent"]
            ):
                validation["warnings"].append("Product may be too drying for dry skin")
                validation["suitability_score"] -= 15

        # Check condition targeting
        if conditions:
            targeted_conditions = 0
            for condition in conditions:
                if self._product_targets_condition(product, condition):
                    targeted_conditions += 1

            if targeted_conditions == 0:
                validation["warnings"].append("Product may not target your specific skin concerns")
                validation["suitability_score"] -= 25

        validation["suitability_score"] = max(0, validation["suitability_score"])
        validation["is_suitable"] = validation["suitability_score"] >= 70

        return validation

    def _product_targets_condition(self, product: Dict[str, Any], condition: str) -> bool:
        """Check if product targets a specific condition"""
        product_name = product.get("name", "").lower()
        product_ingredients = product.get("ingredients", "").lower()
        product_conditions = product.get("skin_conditions", [])

        # Check if condition is explicitly listed
        if condition.lower() in [c.lower() for c in product_conditions]:
            return True

        # Check ingredient-based targeting
        condition_ingredients = {
            "acne": ["salicylic", "niacinamide", "benzoyl"],
            "dark_spots": ["vitamin c", "arbutin", "glycolic"],
            "wrinkles": ["retinol", "peptides", "vitamin c"],
            "dry_skin": ["hyaluronic", "glycerin", "ceramides"],
            "oily_skin": ["niacinamide", "salicylic", "clay"],
        }

        if condition.lower() in condition_ingredients:
            target_ingredients = condition_ingredients[condition.lower()]
            return any(ingredient in product_ingredients for ingredient in target_ingredients)

        return False


# Create global instance
validation_service = SkincareValidationService()
