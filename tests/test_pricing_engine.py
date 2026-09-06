import json
import unittest

from app.services.pricing import calculate_pricing, load_market_references


class PricingEngineTests(unittest.TestCase):
    def setUp(self):
        self.input = {
            "product_id": "ART-001",
            "currency": "INR",
            "product": {"category": "Handmade Bags", "material": "Cotton", "craft_type": "Handwoven"},
            "artisan_costs": {
                "material": 300, "labour_hours": 4, "labour_rate_per_hour": 50,
                "packaging": 30, "other": 20, "desired_margin_percent": 25,
            },
            "market_references": [
                {"category": "handmade bags", "material": "cotton", "craft_type": "handwoven", "price": 850, "source": "local survey"},
                {"category": "handmade bags", "material": None, "craft_type": "handwoven", "price": 950, "source": "catalogue"},
                {"category": "handmade bags", "material": "leather", "craft_type": "hand stitched", "price": 1400, "source": "catalogue"},
            ],
        }

    def test_returns_explainable_cost_market_and_range(self):
        result = calculate_pricing(self.input)
        pricing = result["pricing"]
        self.assertEqual(result["product_id"], "ART-001")
        self.assertEqual(pricing["costs"], {"material": 300.0, "labour": 200.0, "packaging": 30.0, "other": 20.0, "total": 550.0})
        self.assertEqual(pricing["market_reference"], {"sample_size": 2, "minimum": 850.0, "maximum": 950.0, "median": 900.0, "sources": ["local survey", "catalogue"]})
        self.assertEqual(pricing["suggested_price"], {"minimum": 740.0, "maximum": 990.0})
        self.assertEqual(pricing["currency"], "INR")
        self.assertEqual(pricing["margin_type"], "gross_margin")
        self.assertEqual(pricing["confidence"], 0.7)
        self.assertEqual(pricing["market_viability"]["status"], "below_market_range")
        self.assertTrue(pricing["explanation"])
        json.dumps(result, ensure_ascii=False)

    def test_uses_cost_based_range_when_no_market_records_match(self):
        self.input["market_references"] = []
        pricing = calculate_pricing(self.input)["pricing"]
        self.assertEqual(pricing["market_reference"]["sample_size"], 0)
        self.assertIsNone(pricing["market_reference"]["median"])
        self.assertEqual(pricing["suggested_price"], {"minimum": 740.0, "maximum": 810.0})
        self.assertEqual(pricing["confidence"], 0.35)
        self.assertEqual(pricing["market_viability"]["status"], "no_market_data")

    def test_rejects_missing_or_impossible_cost_inputs(self):
        del self.input["artisan_costs"]["other"]
        with self.assertRaisesRegex(ValueError, "artisan_costs.other is required"):
            calculate_pricing(self.input)
        self.input["artisan_costs"]["other"] = 0
        self.input["artisan_costs"]["desired_margin_percent"] = 100
        with self.assertRaisesRegex(ValueError, "less than 100"):
            calculate_pricing(self.input)

    def test_flags_floor_above_market_range(self):
        self.input["market_references"] = [
            {"category": "handmade bags", "material": "cotton", "craft_type": "handwoven", "price": 500, "source": "approved survey"}
        ]
        pricing = calculate_pricing(self.input)["pricing"]
        self.assertEqual(pricing["market_viability"]["status"], "above_market_range")

    def test_default_dataset_is_deliberately_empty_and_valid(self):
        self.assertEqual(load_market_references(), [])

    def test_rejects_market_record_without_reviewable_source(self):
        self.input["market_references"][0].pop("source")
        with self.assertRaisesRegex(ValueError, "source must be a non-empty string"):
            calculate_pricing(self.input)

    def test_returns_no_market_data_when_product_category_is_unavailable(self):
        self.input["product"]["category"] = None
        pricing = calculate_pricing(self.input)["pricing"]
        self.assertEqual(pricing["market_reference"]["sample_size"], 0)
        self.assertEqual(pricing["market_viability"]["status"], "no_market_data")

    def test_excludes_incompatible_comparables_instead_of_falling_back(self):
        self.input["market_references"] = [
            {"category": "handmade bags", "material": "leather", "craft_type": "hand stitched", "price": 1400, "source": "approved survey"}
        ]
        pricing = calculate_pricing(self.input)["pricing"]
        self.assertEqual(pricing["market_reference"]["sample_size"], 0)

    def test_all_zero_costs_remain_zero_only_when_artisan_entered_zeros(self):
        self.input["artisan_costs"] = {
            "material": 0, "labour_hours": 0, "labour_rate_per_hour": 0,
            "packaging": 0, "other": 0, "desired_margin_percent": 25,
        }
        pricing = calculate_pricing(self.input)["pricing"]
        self.assertEqual(pricing["costs"]["total"], 0.0)
        self.assertEqual(pricing["suggested_price"]["minimum"], 0.0)

    def test_rejects_an_implicit_or_unsupported_currency(self):
        del self.input["currency"]
        with self.assertRaisesRegex(ValueError, "currency must be INR"):
            calculate_pricing(self.input)
        self.input["currency"] = "USD"
        with self.assertRaisesRegex(ValueError, "currency must be INR"):
            calculate_pricing(self.input)


if __name__ == "__main__":
    unittest.main()
