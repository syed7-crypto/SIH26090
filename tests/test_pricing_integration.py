import unittest

from app.services.pricing import (
    calculate_pricing,
    map_voice_product_to_pricing_input,
    map_voice_result_to_pricing_input,
)
from app.services.speech import ProductInfo, VoiceMetadata, VoiceProcessingResult


class PricingMapperTests(unittest.TestCase):
    def setUp(self):
        self.costs = {
            "material": 300, "labour_hours": 4, "labour_rate_per_hour": 100,
            "packaging": 0, "other": 0, "desired_margin_percent": 25,
        }

    def test_maps_voice_product_info_without_reimplementing_extraction(self):
        product = ProductInfo(category="handmade bags", material="cotton", craft_type="handwoven")
        pricing_input = map_voice_product_to_pricing_input("ART-VOICE-1", product, self.costs)
        self.assertEqual(pricing_input["product"], {"category": "handmade bags", "material": "cotton", "craft_type": "handwoven"})
        self.assertEqual(calculate_pricing(pricing_input)["status"], "priced")

    def test_maps_voice_processing_result_dictionary(self):
        result = VoiceProcessingResult(
            product_id="ART-VOICE-2",
            product=ProductInfo(category="handmade bags", material="cotton", craft_type="handwoven"),
            voice=VoiceMetadata(),
        )
        pricing_input = map_voice_result_to_pricing_input(result.to_dict(), self.costs)
        self.assertEqual(pricing_input["product_id"], "ART-VOICE-2")
        self.assertEqual(pricing_input["product"]["craft_type"], "handwoven")

    def test_mapper_preserves_missing_costs_for_targeted_response(self):
        pricing_input = map_voice_product_to_pricing_input(
            "ART-VOICE-3", {"category": "bags", "material": "silk", "craft_type": None},
            {"material": 300, "labour_hours": 4},
        )
        result = calculate_pricing(pricing_input)
        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(result["missing_inputs"], ["labour_rate_per_hour", "packaging", "other", "desired_margin_percent"])


class PricingApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        from app.main import app
        cls.client = TestClient(app)

    def payload(self):
        return {
            "currency": "INR",
            "product": {"category": "handmade bags", "material": "cotton", "craft_type": "handwoven"},
            "artisan_costs": {"material": 300, "labour_hours": 4, "labour_rate_per_hour": 100, "packaging": 0, "other": 0, "desired_margin_percent": 25},
        }

    def test_complete_input_returns_priced_result_with_no_market_data(self):
        response = self.client.post("/api/v1/products/ART-API-1/pricing/analyze", json=self.payload())
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "priced")
        self.assertEqual(body["pricing"]["market_viability"]["status"], "no_market_data")

    def test_missing_input_is_successful_targeted_response(self):
        payload = self.payload()
        del payload["artisan_costs"]["labour_rate_per_hour"]
        response = self.client.post("/api/v1/products/ART-API-2/pricing/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["missing_inputs"], ["labour_rate_per_hour"])
        self.assertEqual(response.json()["targeted_questions"][0]["field"], "labour_rate_per_hour")
        self.assertIsNone(response.json()["financial_breakdown"])

    def test_validation_error_is_422(self):
        payload = self.payload()
        payload["artisan_costs"]["material"] = -1
        response = self.client.post("/api/v1/products/ART-API-3/pricing/analyze", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("finite non-negative", response.json()["detail"])

    def test_supplied_market_records_preserve_sources(self):
        payload = self.payload()
        payload["market_references"] = [{"category": "handmade bags", "material": "cotton", "craft_type": "handwoven", "price": 1200, "source": "approved survey"}]
        response = self.client.post("/api/v1/products/ART-API-4/pricing/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["pricing"]["market_reference"]["sources"], ["approved survey"])


if __name__ == "__main__":
    unittest.main()
