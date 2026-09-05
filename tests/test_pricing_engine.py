import json
import unittest

from app.services.pricing import calculate_pricing, load_market_references


class PricingEngineTests(unittest.TestCase):
    def setUp(self):
        self.input = {
            "product_id": "ART-001",
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
        self.assertEqual(pricing["market_reference"], {"sample_size": 2, "minimum": 850.0, "maximum": 950.0, "median": 900.0})
        self.assertEqual(pricing["suggested_price"], {"minimum": 733.33, "maximum": 990.0})
        self.assertEqual(pricing["confidence"], 0.7)
        self.assertEqual(pricing["market_viability"]["status"], "below_market_range")
        self.assertTrue(pricing["explanation"])
        json.dumps(result, ensure_ascii=False)

    def test_uses_cost_based_range_when_no_market_records_match(self):
        self.input["market_references"] = []
        pricing = calculate_pricing(self.input)["pricing"]
        self.assertEqual(pricing["market_reference"]["sample_size"], 0)
        self.assertIsNone(pricing["market_reference"]["median"])
        self.assertEqual(pricing["suggested_price"], {"minimum": 733.33, "maximum": 806.67})
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


if __name__ == "__main__":
    unittest.main()
