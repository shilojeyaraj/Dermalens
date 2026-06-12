"""Unit tests for the SkincareValidationService pure-logic helpers."""


class TestIngredientExtraction:
    def test_extracts_known_ingredient_keywords(self, validator):
        ingredients = validator._extract_ingredients_from_product(
            "Salicylic Acid + Niacinamide Serum"
        )
        assert "salicylic" in ingredients
        assert "niacinamide" in ingredients

    def test_returns_empty_for_unrecognized_product(self, validator):
        assert validator._extract_ingredients_from_product("Plain Water Mist") == []


class TestSafetyScore:
    def test_deducts_5_per_warning_and_15_per_error(self, validator):
        morning = {"warnings": ["a", "b"], "errors": []}
        evening = {"warnings": [], "errors": ["x"]}
        # 100 - (2 * 5) - (1 * 15) = 75
        assert validator._calculate_safety_score(morning, evening) == 75

    def test_score_never_goes_below_zero(self, validator):
        morning = {"warnings": [], "errors": ["e"] * 20}
        evening = {"warnings": [], "errors": []}
        assert validator._calculate_safety_score(morning, evening) == 0


class TestConditionTargeting:
    def test_product_targets_condition_by_ingredient(self, validator):
        product = {"name": "Acne Serum", "ingredients": "salicylic acid 2%"}
        assert validator._product_targets_condition(product, "acne") is True

    def test_product_does_not_target_unrelated_condition(self, validator):
        product = {"name": "Acne Serum", "ingredients": "salicylic acid 2%"}
        assert validator._product_targets_condition(product, "wrinkles") is False

    def test_product_targets_condition_when_explicitly_listed(self, validator):
        product = {"name": "Mystery Cream", "ingredients": "", "skin_conditions": ["Acne"]}
        # Match is case-insensitive
        assert validator._product_targets_condition(product, "acne") is True


class TestProductRecommendationValidation:
    def test_flags_irritant_for_sensitive_skin(self, validator):
        product = {"name": "Toner", "ingredients": "alcohol, fragrance"}
        profile = {"skin_type": "sensitive", "concerns": []}
        result = validator.validate_product_recommendation(product, profile)

        assert result["suitability_score"] == 80  # 100 - 20 irritant penalty
        assert result["is_suitable"] is True  # still >= 70 threshold
        assert any("sensitive skin" in w.lower() for w in result["warnings"])

    def test_unsuitable_when_irritating_and_off_target(self, validator):
        product = {"name": "Random Cream", "ingredients": "alcohol"}
        profile = {"skin_type": "sensitive", "concerns": ["acne"]}
        result = validator.validate_product_recommendation(product, profile)

        # -20 (sensitive irritant) and -25 (does not target acne) -> 55
        assert result["suitability_score"] == 55
        assert result["is_suitable"] is False
