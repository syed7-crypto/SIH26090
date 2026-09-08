import unittest
from datetime import datetime, timezone

from app.services.pricing import calculate_pricing, map_voice_product_to_pricing_input
from app.services.pricing.trend_analyzer import analyze_market_trend


def base_input():
    return {
        "product_id": "ART-V2",
        "currency": "INR",
        "product": {
            "category": "bags",
            "subcategory": "tote",
            "material": "cotton",
            "craft_type": "handwoven",
        },
        "artisan_costs": {
            "material": 300,
            "labour_hours": 4,
            "labour_rate_per_hour": 100,
            "packaging": 20,
            "other": 10,
            "desired_margin_percent": 25,
        },
        "market_references": [],
    }


class PricingV2Tests(unittest.TestCase):
    def test_positioning_is_optional_and_bounded(self):
        result = calculate_pricing(base_input())
        self.assertFalse(result["pricing"]["product_positioning"]["available"])

        data = base_input()
        data["product"].update({"craft_complexity": 100, "craftsmanship_level": "high"})
        positioning = calculate_pricing(data)["pricing"]["product_positioning"]
        self.assertEqual(positioning["adjustment_percent"], 10.0)

    def test_positioning_never_reduces_cost_floor(self):
        data = base_input()
        data["product"].update({"craft_complexity": 80, "craftsmanship_level": "high"})
        result = calculate_pricing(data)["pricing"]
        self.assertGreaterEqual(
            result["suggested_price"]["minimum"],
            result["financial_terms"]["cost_recovery"],
        )

    def test_positioning_validation_is_deterministic(self):
        data = base_input()
        data["product"]["craft_complexity"] = 101
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            calculate_pricing(data)
        data["product"]["craft_complexity"] = 50
        data["product"]["craftsmanship_level"] = "unknown"
        with self.assertRaisesRegex(ValueError, "low, medium, or high"):
            calculate_pricing(data)

    def test_photo_evidence_affects_confidence_only(self):
        without_photo = calculate_pricing(base_input())["pricing"]
        data = base_input()
        data["product"]["photo_quality_score"] = 90
        with_photo = calculate_pricing(data)["pricing"]
        self.assertEqual(without_photo["suggested_price"], with_photo["suggested_price"])
        self.assertEqual(with_photo["photo_evidence"]["band"], "strong")
        self.assertIn("visual evidence", with_photo["confidence"]["reason"])

    def test_financial_terms_use_non_labour_costs_without_inventing_reinvestment(self):
        terms = calculate_pricing(base_input())["pricing"]["financial_terms"]
        self.assertEqual(terms["non_labour_costs"], 330.0)
        self.assertNotIn("reinvestment_amount", terms)

    def test_poor_photo_evidence_does_not_lower_cost_floor(self):
        data = base_input()
        data["product"]["photo_readiness"] = {"score": 20}
        result = calculate_pricing(data)["pricing"]
        self.assertEqual(result["photo_evidence"]["band"], "weak")
        self.assertGreaterEqual(result["suggested_price"]["minimum"], 570)

    def test_market_trends(self):
        rising = [{"price": price, "period": period} for price, period in ((100, "2024-01-01"), (110, "2024-02-01"), (130, "2024-03-01"), (140, "2024-04-01"))]
        falling = [{"price": price, "period": period} for price, period in ((140, "2024-01-01"), (130, "2024-02-01"), (110, "2024-03-01"), (100, "2024-04-01"))]
        stable = [{"price": price, "period": period} for price, period in ((100, "2024-01-01"), (100, "2024-02-01"), (103, "2024-03-01"), (103, "2024-04-01"))]
        self.assertEqual(analyze_market_trend(rising)["direction"], "rising")
        self.assertEqual(analyze_market_trend(falling)["direction"], "falling")
        self.assertEqual(analyze_market_trend(stable)["direction"], "stable")
        self.assertEqual(analyze_market_trend(rising[:3])["direction"], "insufficient_data")

    def test_trend_changes_only_the_bounded_upper_range(self):
        rising = base_input()
        rising["market_references"] = [
            {"category": "bags", "price": price, "period": period, "source": "survey"}
            for price, period in ((800, "2024-01-01"), (800, "2024-02-01"), (1000, "2024-03-01"), (1000, "2024-04-01"))
        ]
        falling = {**base_input(), "market_references": [
            {"category": "bags", "price": price, "period": period, "source": "survey"}
            for price, period in ((1000, "2024-01-01"), (1000, "2024-02-01"), (800, "2024-03-01"), (800, "2024-04-01"))
        ]}
        rising_result = calculate_pricing(rising)["pricing"]
        falling_result = calculate_pricing(falling)["pricing"]
        self.assertEqual(rising_result["market_trend"]["pricing_adjustment_percent"], 3.0)
        self.assertEqual(falling_result["market_trend"]["pricing_adjustment_percent"], -3.0)
        self.assertGreater(rising_result["suggested_price"]["maximum"], falling_result["suggested_price"]["maximum"])
        self.assertEqual(rising_result["suggested_price"]["minimum"], 980.0)
        self.assertEqual(falling_result["suggested_price"]["minimum"], 980.0)

    def test_stable_and_insufficient_trends_do_not_change_range(self):
        stable = base_input()
        stable["market_references"] = [
            {"category": "bags", "price": price, "period": period, "source": "survey"}
            for price, period in ((900, "2024-01-01"), (900, "2024-02-01"), (920, "2024-03-01"), (920, "2024-04-01"))
        ]
        without_trend = {**base_input(), "market_references": [
            {"category": "bags", "price": 910, "source": "survey"},
        ]}
        stable_result = calculate_pricing(stable)["pricing"]
        no_trend_result = calculate_pricing(without_trend)["pricing"]
        self.assertEqual(stable_result["market_trend"]["direction"], "stable")
        self.assertEqual(stable_result["market_trend"]["pricing_adjustment_percent"], 0.0)
        self.assertEqual(stable_result["suggested_price"]["maximum"], no_trend_result["suggested_price"]["maximum"])

        insufficient = base_input()
        insufficient["market_references"] = [
            {"category": "bags", "price": 910, "period": "2024-01-01", "source": "survey"},
            {"category": "bags", "price": 910, "period": "2024-02-01", "source": "survey"},
            {"category": "bags", "price": 910, "period": "2024-03-01", "source": "survey"},
        ]
        self.assertEqual(calculate_pricing(insufficient)["pricing"]["market_trend"]["pricing_adjustment_percent"], 0.0)

    def test_trend_calculation_is_deterministic_and_never_reduces_floor(self):
        data = base_input()
        data["market_references"] = [
            {"category": "bags", "price": price, "period": period, "source": "survey"}
            for price, period in ((1200, "2024-01-01"), (1200, "2024-02-01"), (800, "2024-03-01"), (800, "2024-04-01"))
        ]
        first = calculate_pricing(data)
        second = calculate_pricing(data)
        self.assertEqual(first, second)
        self.assertEqual(first["pricing"]["suggested_price"]["minimum"], 980.0)
        self.assertLessEqual(abs(first["pricing"]["market_trend"]["pricing_adjustment_percent"]), 3.0)

    def test_market_trend_ignores_invalid_and_missing_dates(self):
        result = analyze_market_trend([
            {"price": 100, "period": "not-a-date"},
            {"price": 110, "period": "2024-02-01"},
            {"price": 120},
            {"price": 130, "period": "2024-04-01"},
        ])
        self.assertEqual(result["direction"], "insufficient_data")
        self.assertEqual(result["sample_size"], 2)

    def test_market_trend_handles_period_date_fallback_and_mixed_timezones(self):
        records = [
            {"price": 100, "period": None, "date": "2024-01-01"},
            {"price": 100, "date": datetime(2024, 2, 1)},
            {"price": 120, "period": "2024-03-01T00:00:00"},
            {"price": 120, "period": "2024-04-01T00:00:00Z"},
        ]
        result = analyze_market_trend(records)
        self.assertEqual(result["direction"], "rising")
        self.assertEqual(result["sample_size"], 4)
        self.assertEqual(
            analyze_market_trend([
                {"price": 100, "period": datetime(2024, 1, 1, tzinfo=timezone.utc)},
                {"price": 100, "period": "2024-02-01"},
                {"price": 120, "period": "2024-03-01T00:00:00Z"},
                {"price": 120, "period": "2024-04-01"},
            ])["direction"],
            "rising",
        )

    def test_market_trend_is_returned_for_comparables(self):
        data = base_input()
        data["market_references"] = [
            {"category": "bags", "subcategory": "tote", "material": "cotton", "craft_type": "handwoven", "price": price, "period": period, "source": "survey"}
            for price, period in ((800, "2024-01-01"), (820, "2024-02-01"), (1000, "2024-03-01"), (1020, "2024-04-01"))
        ]
        pricing = calculate_pricing(data)["pricing"]
        self.assertEqual(pricing["market_matching_basis"], "category + material + craft_type")
        self.assertEqual(pricing["market_reference"]["sample_size"], 4)
        self.assertEqual(pricing["market_trend"]["direction"], "rising")

    def test_subcategory_matching_and_incompatible_category(self):
        data = base_input()
        data["product"] = {"category": "bags", "subcategory": "tote"}
        data["market_references"] = [
            {"category": "bags", "subcategory": "tote", "price": 900, "source": "tote survey"},
            {"category": "jewellery", "subcategory": "tote", "price": 9999, "source": "wrong category"},
        ]
        pricing = calculate_pricing(data)["pricing"]
        self.assertEqual(pricing["market_matching_basis"], "category + subcategory")
        self.assertEqual(pricing["market_reference"]["sample_size"], 1)

    def test_expanded_voice_mapping_preserves_real_attributes_only(self):
        mapped = map_voice_product_to_pricing_input(
            "ART-MAP",
            {
                "name": "woven tote",
                "category": "bags",
                "subcategory": "tote",
                "material": "cotton",
                "color": "blue",
                "pattern": "floral",
                "dimensions": {"length": 6, "unit": "ft"},
                "craft_complexity": 70,
            },
            {},
        )
        self.assertEqual(mapped["product"]["color"], "blue")
        self.assertEqual(mapped["product"]["dimensions"]["length"], 6)
        self.assertEqual(mapped["product"]["craft_complexity"], 70)
        self.assertNotIn("craftsmanship_level", mapped["product"])

    def test_invalid_numeric_and_market_records_are_rejected(self):
        data = base_input()
        data["artisan_costs"]["material"] = "not-a-number"
        with self.assertRaisesRegex(ValueError, "must be a number"):
            calculate_pricing(data)
        data = base_input()
        data["market_references"] = [{"category": "bags", "price": "nan", "source": "bad"}]
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            calculate_pricing(data)


if __name__ == "__main__":
    unittest.main()
