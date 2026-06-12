"""Integration tests exercising the full routine-validation flow end to end."""


def _dry_skin_profile():
    return {"skin_type": "dry", "concerns": ["dry_skin"]}


class TestValidateSkincareRoutine:
    def test_full_routine_validation_shape_and_scores(self, validator):
        routine = {
            "morning_routine": [
                {"action": "cleanser", "product": "Gentle Hydrating Cleanser"},
                {"action": "moisturizer", "product": "Hyaluronic Acid Moisturizer"},
            ],
            "evening_routine": [
                {"action": "cleanser", "product": "Gentle Cleanser"},
                {"action": "moisturizer", "product": "Glycerin Night Cream"},
            ],
        }

        result = validator.validate_skincare_routine(routine, _dry_skin_profile())

        # Result contract
        for key in (
            "is_valid",
            "warnings",
            "errors",
            "recommendations",
            "safety_score",
            "effectiveness_score",
        ):
            assert key in result

        assert isinstance(result["warnings"], list)
        assert result["is_valid"] is True  # no hard errors in a valid routine
        assert 0 <= result["safety_score"] <= 100
        assert 0 <= result["effectiveness_score"] <= 100
        # Cleanser + moisturizer + dry-skin targeting -> a meaningful (non-trivial) score
        assert result["effectiveness_score"] >= 50

    def test_warns_when_morning_routine_has_no_sunscreen(self, validator):
        routine = {
            "morning_routine": [
                {"action": "cleanser", "product": "Gentle Cleanser"},
            ],
            "evening_routine": [],
        }

        result = validator.validate_skincare_routine(routine, _dry_skin_profile())

        assert any("sunscreen" in w.lower() for w in result["warnings"])

    def test_no_sunscreen_warning_when_spf_present(self, validator):
        routine = {
            "morning_routine": [
                {"action": "cleanser", "product": "Gentle Cleanser"},
                {"action": "sunscreen", "product": "SPF 50 Daily Sunscreen"},
            ],
            "evening_routine": [],
        }

        result = validator.validate_skincare_routine(routine, _dry_skin_profile())

        assert not any("should include sunscreen" in w.lower() for w in result["warnings"])
