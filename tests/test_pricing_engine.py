import unittest

from app.services.pricing import calculate_pricing, load_market_references


class PricingEngineTests(unittest.TestCase):
    def setUp(self):
        self.input = {
            "product_id": "ART-001", "currency": "INR",
            "product": {"category": "Handmade Bags", "material": "Cotton", "craft_type": "Handwoven"},
            "artisan_costs": {"material": 300, "labour_hours": 4, "labour_rate_per_hour": 50, "packaging": 30, "other": 20, "desired_margin_percent": 25},
            "market_references": [{"category": "handmade bags", "material": "cotton", "craft_type": "handwoven", "price": 850, "source": "local survey"}],
        }

    def pricing(self):
        return calculate_pricing(self.input)["pricing"]

    def test_normal_pricing_uses_transparent_gross_margin_formula(self):
        pricing = self.pricing()
        self.assertEqual(pricing["costs"]["total"], 550.0)
        self.assertEqual(pricing["suggested_price"]["minimum"], 740.0)
        self.assertEqual(pricing["market_matching_basis"], "category + material + craft_type")

    def test_market_summary_preserves_selected_sources_regression(self):
        self.input["market_references"].append({"category": "handmade bags", "material": "cotton", "craft_type": "handwoven", "price": 950, "source": "catalogue"})
        market = self.pricing()["market_reference"]
        self.assertEqual(market, {"sample_size": 2, "minimum": 850.0, "maximum": 950.0, "median": 900.0, "sources": ["local survey", "catalogue"]})

    def test_no_market_data_is_honest_and_cost_based(self):
        self.input["market_references"] = []
        pricing = self.pricing()
        self.assertEqual(pricing["market_reference"], {"sample_size": 0, "minimum": None, "maximum": None, "median": None, "sources": []})
        self.assertEqual(pricing["market_viability"]["status"], "no_market_data")
        self.assertEqual(pricing["suggested_price"], {"minimum": 740.0, "maximum": 810.0})
        self.assertTrue(any("cost-and-margin based only" in message for message in pricing["explanation"]))

    def test_missing_labour_rate_is_structured_not_guessed(self):
        del self.input["artisan_costs"]["labour_rate_per_hour"]
        self.assertEqual(calculate_pricing(self.input), {"product_id": "ART-001", "status": "needs_input", "missing_inputs": ["labour_rate_per_hour"]})

    def test_missing_packaging_and_margin_are_not_zero_or_25_percent(self):
        del self.input["artisan_costs"]["packaging"]
        del self.input["artisan_costs"]["desired_margin_percent"]
        result = calculate_pricing(self.input)
        self.assertEqual(result["missing_inputs"], ["packaging", "desired_margin_percent"])

    def test_negative_cost_is_rejected(self):
        self.input["artisan_costs"]["other"] = -1
        with self.assertRaisesRegex(ValueError, "finite non-negative"):
            calculate_pricing(self.input)

    def test_margin_at_or_over_100_is_rejected(self):
        self.input["artisan_costs"]["desired_margin_percent"] = 100
        with self.assertRaisesRegex(ValueError, "less than 100"):
            calculate_pricing(self.input)

    def test_unsupported_currency_is_rejected(self):
        self.input["currency"] = "USD"
        with self.assertRaisesRegex(ValueError, "currency must be INR"):
            calculate_pricing(self.input)

    def test_exact_category_material_and_craft_match_is_preferred(self):
        self.input["market_references"].append({"category": "handmade bags", "material": "cotton", "craft_type": None, "price": 900, "source": "broader"})
        self.assertEqual(self.pricing()["market_reference"]["sample_size"], 1)

    def test_category_and_material_match_when_no_exact_match(self):
        self.input["market_references"] = [{"category": "handmade bags", "material": "cotton", "craft_type": None, "price": 900, "source": "survey"}]
        pricing = self.pricing()
        self.assertEqual(pricing["market_matching_basis"], "category + material")

    def test_category_only_match_when_appropriate(self):
        self.input["product"] = {"category": "handmade bags"}
        self.input["market_references"] = [{"category": "handmade bags", "material": None, "craft_type": None, "price": 900, "source": "survey"}]
        self.assertEqual(self.pricing()["market_matching_basis"], "category only")

    def test_explicitly_incompatible_attributes_never_become_comparables(self):
        self.input["market_references"] = [{"category": "handmade bags", "material": "leather", "craft_type": "hand stitched", "price": 1400, "source": "survey"}]
        self.assertEqual(self.pricing()["market_viability"]["status"], "no_market_data")

    def test_target_above_market_range_is_reported_without_lowering_floor(self):
        self.input["market_references"][0]["price"] = 500
        pricing = self.pricing()
        self.assertEqual(pricing["market_viability"]["status"], "above_market_range")
        self.assertGreaterEqual(pricing["suggested_price"]["minimum"], 733.34)

    def test_target_below_market_range_is_reported(self):
        pricing = self.pricing()
        self.assertEqual(pricing["market_viability"]["status"], "below_market_range")

    def test_all_zero_costs_require_explicit_zeros(self):
        self.input["artisan_costs"] = {"material": 0, "labour_hours": 0, "labour_rate_per_hour": 0, "packaging": 0, "other": 0, "desired_margin_percent": 25}
        self.assertEqual(self.pricing()["costs"]["total"], 0.0)
        del self.input["artisan_costs"]["other"]
        self.assertIn("other", calculate_pricing(self.input)["missing_inputs"])

    def test_market_source_is_preserved(self):
        self.assertEqual(self.pricing()["market_reference"]["sources"], ["local survey"])

    def test_suggested_price_never_falls_below_margin_floor(self):
        self.input["market_references"][0]["price"] = 100
        self.assertGreaterEqual(self.pricing()["suggested_price"]["minimum"], 733.34)

    def test_default_dataset_is_deliberately_empty(self):
        self.assertEqual(load_market_references(), [])

    def test_market_source_is_required(self):
        del self.input["market_references"][0]["source"]
        with self.assertRaisesRegex(ValueError, "source must be a non-empty string"):
            calculate_pricing(self.input)


if __name__ == "__main__":
    unittest.main()
