#!/usr/bin/env python3
"""
Ingredient Database Service
Comprehensive database of skincare ingredients with their properties and interactions
"""
import json
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class IngredientDatabase:
    """Database of skincare ingredients with properties and interactions"""
    
    def __init__(self):
        self.ingredients = {}
        self.condition_ingredients = {}
        self.skin_type_ingredients = {}
        self.ingredient_interactions = {}
        self._load_ingredient_data()
    
    def _load_ingredient_data(self):
        """Load ingredient data from JSON file or create default data"""
        try:
            data_file = Path("data/ingredients.json")
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.ingredients = data.get("ingredients", {})
                    self.condition_ingredients = data.get("condition_ingredients", {})
                    self.skin_type_ingredients = data.get("skin_type_ingredients", {})
                    self.ingredient_interactions = data.get("ingredient_interactions", {})
            else:
                self._create_default_ingredient_data()
                self._save_ingredient_data()
            
            logger.info(f"Loaded {len(self.ingredients)} ingredients")
            
        except Exception as e:
            logger.error(f"Error loading ingredient data: {e}")
            self._create_default_ingredient_data()
    
    def _create_default_ingredient_data(self):
        """Create default ingredient database"""
        self.ingredients = {
            # Acids
            "salicylic_acid": {
                "name": "Salicylic Acid",
                "category": "BHA",
                "benefits": ["acne", "blackheads", "oily_skin", "large_pores"],
                "skin_types": ["oily", "combination"],
                "concentration_range": "0.5-2%",
                "usage": "night",
                "frequency": "daily",
                "interactions": ["retinol", "vitamin_c"],
                "warnings": ["sensitive_skin", "pregnancy"],
                "description": "Beta-hydroxy acid that exfoliates inside pores"
            },
            "glycolic_acid": {
                "name": "Glycolic Acid",
                "category": "AHA",
                "benefits": ["dark_spots", "wrinkles", "uneven_texture", "dull_skin"],
                "skin_types": ["normal", "combination", "oily"],
                "concentration_range": "5-10%",
                "usage": "night",
                "frequency": "2-3x_weekly",
                "interactions": ["retinol", "vitamin_c"],
                "warnings": ["sensitive_skin", "pregnancy"],
                "description": "Alpha-hydroxy acid that exfoliates skin surface"
            },
            "lactic_acid": {
                "name": "Lactic Acid",
                "category": "AHA",
                "benefits": ["dry_skin", "wrinkles", "uneven_texture"],
                "skin_types": ["dry", "normal", "sensitive"],
                "concentration_range": "5-10%",
                "usage": "night",
                "frequency": "2-3x_weekly",
                "interactions": ["retinol"],
                "warnings": ["pregnancy"],
                "description": "Gentle AHA that also hydrates skin"
            },
            
            # Vitamins
            "vitamin_c": {
                "name": "Vitamin C (Ascorbic Acid)",
                "category": "antioxidant",
                "benefits": ["dark_spots", "hyperpigmentation", "wrinkles", "dull_skin"],
                "skin_types": ["all"],
                "concentration_range": "10-20%",
                "usage": "morning",
                "frequency": "daily",
                "interactions": ["niacinamide", "retinol"],
                "warnings": ["sensitive_skin"],
                "description": "Powerful antioxidant that brightens and protects skin"
            },
            "niacinamide": {
                "name": "Niacinamide",
                "category": "vitamin",
                "benefits": ["acne", "oily_skin", "large_pores", "uneven_texture"],
                "skin_types": ["all"],
                "concentration_range": "2-10%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": ["vitamin_c"],
                "warnings": [],
                "description": "Vitamin B3 that controls oil and improves texture"
            },
            "retinol": {
                "name": "Retinol",
                "category": "vitamin_a",
                "benefits": ["wrinkles", "acne", "uneven_texture", "dull_skin"],
                "skin_types": ["normal", "combination", "oily"],
                "concentration_range": "0.1-1%",
                "usage": "night",
                "frequency": "2-3x_weekly",
                "interactions": ["vitamin_c", "acids"],
                "warnings": ["sensitive_skin", "pregnancy", "sun_exposure"],
                "description": "Vitamin A derivative that accelerates cell turnover"
            },
            
            # Hydrating Ingredients
            "hyaluronic_acid": {
                "name": "Hyaluronic Acid",
                "category": "humectant",
                "benefits": ["dry_skin", "wrinkles", "hydration"],
                "skin_types": ["all"],
                "concentration_range": "0.1-2%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Powerful humectant that holds 1000x its weight in water"
            },
            "glycerin": {
                "name": "Glycerin",
                "category": "humectant",
                "benefits": ["dry_skin", "hydration"],
                "skin_types": ["all"],
                "concentration_range": "2-15%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Gentle humectant that draws moisture to skin"
            },
            "ceramides": {
                "name": "Ceramides",
                "category": "barrier_repair",
                "benefits": ["dry_skin", "sensitive_skin", "barrier_repair"],
                "skin_types": ["dry", "sensitive", "normal"],
                "concentration_range": "0.5-5%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Lipids that strengthen skin barrier"
            },
            
            # Soothing Ingredients
            "aloe_vera": {
                "name": "Aloe Vera",
                "category": "soothing",
                "benefits": ["sensitive_skin", "dry_skin", "inflammation"],
                "skin_types": ["all"],
                "concentration_range": "1-10%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Natural soothing and hydrating ingredient"
            },
            "centella_asiatica": {
                "name": "Centella Asiatica (Cica)",
                "category": "soothing",
                "benefits": ["sensitive_skin", "inflammation", "wound_healing"],
                "skin_types": ["sensitive", "all"],
                "concentration_range": "0.1-5%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Traditional herb with anti-inflammatory properties"
            },
            "chamomile": {
                "name": "Chamomile",
                "category": "soothing",
                "benefits": ["sensitive_skin", "inflammation", "calming"],
                "skin_types": ["sensitive", "all"],
                "concentration_range": "0.1-2%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": ["allergic_reactions"],
                "description": "Gentle botanical with anti-inflammatory properties"
            },
            
            # Oils
            "jojoba_oil": {
                "name": "Jojoba Oil",
                "category": "oil",
                "benefits": ["dry_skin", "hydration", "barrier_repair"],
                "skin_types": ["dry", "normal", "combination"],
                "concentration_range": "1-10%",
                "usage": "night",
                "frequency": "daily",
                "interactions": [],
                "warnings": ["acne_prone"],
                "description": "Non-comedogenic oil similar to skin's natural sebum"
            },
            "argan_oil": {
                "name": "Argan Oil",
                "category": "oil",
                "benefits": ["dry_skin", "wrinkles", "hydration"],
                "skin_types": ["dry", "normal"],
                "concentration_range": "1-5%",
                "usage": "night",
                "frequency": "daily",
                "interactions": [],
                "warnings": ["acne_prone"],
                "description": "Rich oil high in vitamin E and fatty acids"
            },
            "rosehip_oil": {
                "name": "Rosehip Oil",
                "category": "oil",
                "benefits": ["dark_spots", "wrinkles", "dry_skin"],
                "skin_types": ["dry", "normal", "combination"],
                "concentration_range": "1-5%",
                "usage": "night",
                "frequency": "daily",
                "interactions": ["retinol"],
                "warnings": ["acne_prone"],
                "description": "Oil rich in vitamin A and essential fatty acids"
            },
            
            # Peptides
            "peptides": {
                "name": "Peptides",
                "category": "peptide",
                "benefits": ["wrinkles", "firmness", "hydration"],
                "skin_types": ["all"],
                "concentration_range": "0.1-5%",
                "usage": "morning_night",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Amino acid chains that support collagen production"
            },
            
            # Sunscreen
            "zinc_oxide": {
                "name": "Zinc Oxide",
                "category": "sunscreen",
                "benefits": ["sun_protection", "sensitive_skin"],
                "skin_types": ["all"],
                "concentration_range": "5-25%",
                "usage": "morning",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Physical sunscreen that blocks UVA and UVB rays"
            },
            "titanium_dioxide": {
                "name": "Titanium Dioxide",
                "category": "sunscreen",
                "benefits": ["sun_protection", "sensitive_skin"],
                "skin_types": ["all"],
                "concentration_range": "2-25%",
                "usage": "morning",
                "frequency": "daily",
                "interactions": [],
                "warnings": [],
                "description": "Physical sunscreen that blocks UVB rays"
            }
        }
        
        # Condition to ingredients mapping
        self.condition_ingredients = {
            "acne": ["salicylic_acid", "niacinamide", "retinol", "benzoyl_peroxide"],
            "blackheads": ["salicylic_acid", "niacinamide", "glycolic_acid"],
            "whiteheads": ["salicylic_acid", "niacinamide", "retinol"],
            "dark_spots": ["vitamin_c", "glycolic_acid", "lactic_acid", "arbutin"],
            "hyperpigmentation": ["vitamin_c", "glycolic_acid", "arbutin", "retinol"],
            "wrinkles": ["retinol", "peptides", "vitamin_c", "hyaluronic_acid"],
            "dry_skin": ["hyaluronic_acid", "glycerin", "ceramides", "jojoba_oil"],
            "oily_skin": ["niacinamide", "salicylic_acid", "clay", "tea_tree_oil"],
            "sensitive_skin": ["aloe_vera", "centella_asiatica", "chamomile", "ceramides"],
            "normal_skin": ["hyaluronic_acid", "vitamin_c", "peptides", "niacinamide"],
            "rosacea": ["centella_asiatica", "aloe_vera", "niacinamide", "ceramides"],
            "eczema": ["ceramides", "aloe_vera", "centella_asiatica", "oatmeal"],
            "large_pores": ["niacinamide", "salicylic_acid", "clay", "retinol"],
            "uneven_texture": ["glycolic_acid", "lactic_acid", "retinol", "vitamin_c"],
            "dull_skin": ["vitamin_c", "glycolic_acid", "lactic_acid", "peptides"]
        }
        
        # Skin type to ingredients mapping
        self.skin_type_ingredients = {
            "dry": ["hyaluronic_acid", "glycerin", "ceramides", "jojoba_oil", "argan_oil"],
            "oily": ["niacinamide", "salicylic_acid", "clay", "tea_tree_oil", "zinc_oxide"],
            "combination": ["niacinamide", "hyaluronic_acid", "vitamin_c", "peptides"],
            "normal": ["hyaluronic_acid", "vitamin_c", "peptides", "niacinamide"],
            "sensitive": ["aloe_vera", "centella_asiatica", "ceramides", "chamomile"]
        }
        
        # Ingredient interactions
        self.ingredient_interactions = {
            "vitamin_c": {
                "incompatible": ["retinol", "niacinamide"],
                "recommended_separation": "morning_vs_night"
            },
            "retinol": {
                "incompatible": ["vitamin_c", "acids"],
                "recommended_separation": "alternate_nights"
            },
            "acids": {
                "incompatible": ["retinol", "vitamin_c"],
                "recommended_separation": "alternate_nights"
            }
        }
    
    def _save_ingredient_data(self):
        """Save ingredient data to JSON file"""
        try:
            data = {
                "ingredients": self.ingredients,
                "condition_ingredients": self.condition_ingredients,
                "skin_type_ingredients": self.skin_type_ingredients,
                "ingredient_interactions": self.ingredient_interactions
            }
            
            # Create data directory if it doesn't exist
            Path("data").mkdir(exist_ok=True)
            
            with open("data/ingredients.json", 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving ingredient data: {e}")
    
    def get_ingredient_info(self, ingredient_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific ingredient"""
        return self.ingredients.get(ingredient_key)
    
    def get_ingredients_for_condition(self, condition: str) -> List[str]:
        """Get recommended ingredients for a specific skin condition"""
        return self.condition_ingredients.get(condition, [])
    
    def get_ingredients_for_skin_type(self, skin_type: str) -> List[str]:
        """Get recommended ingredients for a specific skin type"""
        return self.skin_type_ingredients.get(skin_type, [])
    
    def get_ingredient_interactions(self, ingredient: str) -> Dict[str, Any]:
        """Get interaction information for an ingredient"""
        return self.ingredient_interactions.get(ingredient, {})
    
    def validate_ingredient_combination(self, ingredients: List[str]) -> Dict[str, Any]:
        """Validate if ingredients can be used together safely"""
        warnings = []
        recommendations = []
        
        for ingredient in ingredients:
            interactions = self.get_ingredient_interactions(ingredient)
            incompatible = interactions.get("incompatible", [])
            
            for other_ingredient in ingredients:
                if other_ingredient != ingredient and other_ingredient in incompatible:
                    warnings.append(f"{ingredient} and {other_ingredient} may not work well together")
                    recommendations.append(interactions.get("recommended_separation", "Use separately"))
        
        return {
            "is_safe": len(warnings) == 0,
            "warnings": warnings,
            "recommendations": recommendations
        }
    
    def get_routine_ingredients(self, conditions: List[str], skin_type: str) -> Dict[str, List[str]]:
        """Get recommended ingredients for a complete skincare routine"""
        routine_ingredients = {
            "cleanser": [],
            "treatment": [],
            "moisturizer": [],
            "sunscreen": []
        }
        
        # Get ingredients for conditions
        condition_ingredients = set()
        for condition in conditions:
            condition_ingredients.update(self.get_ingredients_for_condition(condition))
        
        # Get ingredients for skin type
        skin_type_ingredients = set(self.get_ingredients_for_skin_type(skin_type))
        
        # Combine and categorize
        all_ingredients = condition_ingredients.union(skin_type_ingredients)
        
        for ingredient in all_ingredients:
            ingredient_info = self.get_ingredient_info(ingredient)
            if ingredient_info:
                category = ingredient_info.get("category", "")
                usage = ingredient_info.get("usage", "")
                
                if "cleanser" in category or "cleansing" in ingredient.lower():
                    routine_ingredients["cleanser"].append(ingredient)
                elif "sunscreen" in category or "spf" in ingredient.lower():
                    routine_ingredients["sunscreen"].append(ingredient)
                elif usage == "morning" or "antioxidant" in category:
                    routine_ingredients["treatment"].append(ingredient)
                elif usage == "night" or "acid" in category or "retinol" in ingredient:
                    routine_ingredients["treatment"].append(ingredient)
                else:
                    routine_ingredients["moisturizer"].append(ingredient)
        
        return routine_ingredients
    
    def search_ingredients(self, query: str) -> List[Dict[str, Any]]:
        """Search ingredients by name or benefits"""
        query = query.lower()
        results = []
        
        for key, ingredient in self.ingredients.items():
            name = ingredient.get("name", "").lower()
            benefits = ingredient.get("benefits", [])
            description = ingredient.get("description", "").lower()
            
            if (query in name or 
                any(query in benefit.lower() for benefit in benefits) or 
                query in description):
                results.append({
                    "key": key,
                    "name": ingredient.get("name"),
                    "category": ingredient.get("category"),
                    "benefits": benefits,
                    "description": ingredient.get("description")
                })
        
        return results

# Create global instance
ingredient_database = IngredientDatabase()

