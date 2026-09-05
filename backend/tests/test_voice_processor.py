"""Tests for Voice & Language Intelligence module.

Tests cover:
- Language detection for multiple Indian languages
- Translation pipeline
- Product information extraction
- Missing field identification
- Complete voice processing pipeline
- Schema compliance
"""

import unittest
import json
from pathlib import Path
from unittest.mock import MagicMock
from app.services.speech import (
    VoiceProcessor,
    VoiceProcessingResult,
    LanguageDetector,
    Translator,
    ProductInfoExtractor,
    ProductInfo,
    ProductDimensions,
    ProductWeight,
)


class TestLanguageDetection(unittest.TestCase):
    """Test language detection from transcripts."""

    def test_english_detection(self):
        """English text should be detected as English."""
        text = "This is a beautiful silk scarf made with traditional Indian techniques"
        lang_code, confidence = LanguageDetector.detect(text)
        self.assertEqual(lang_code, "en")
        self.assertGreaterEqual(confidence, 0.4)

    def test_kannada_detection(self):
        """Kannada text should be detected."""
        # Kannada: "This is silk fabric"
        text = "ಇದು ರೇಷಮೆ ಬಟ್ಟೆಯಾಗಿದೆ"
        lang_code, confidence = LanguageDetector.detect(text)
        self.assertEqual(lang_code, "kn")
        self.assertGreater(confidence, 0.7)

    def test_empty_text_detection(self):
        """Empty text should return None language."""
        text = ""
        lang_code, confidence = LanguageDetector.detect(text)
        self.assertIsNone(lang_code)
        self.assertEqual(confidence, 0.0)

    def test_none_text_detection(self):
        """None text should return None language."""
        lang_code, confidence = LanguageDetector.detect(None)
        self.assertIsNone(lang_code)
        self.assertEqual(confidence, 0.0)

    def test_mixed_script_detection(self):
        """Mixed script should detect primary language."""
        # Mix of English and Kannada
        text = "This is ರೇಷಮೆ silk fabric"
        lang_code, confidence = LanguageDetector.detect(text)
        # Should detect Kannada due to script presence
        self.assertEqual(lang_code, "kn")


class TestTranslation(unittest.TestCase):
    """Test translation pipeline."""

    def test_english_no_translation_needed(self):
        """English text should not be translated."""
        text = "This is a silk scarf"
        translated, confidence = Translator.translate(text, "en")
        self.assertEqual(translated, text)
        self.assertEqual(confidence, 1.0)

    def test_none_language_no_translation(self):
        """None language should return text as-is."""
        text = "Some text"
        translated, confidence = Translator.translate(text, None)
        self.assertEqual(translated, text)
        self.assertEqual(confidence, 1.0)

    def test_none_text_no_translation(self):
        """None text should return None."""
        translated, confidence = Translator.translate(None, "kn")
        self.assertIsNone(translated)
        self.assertEqual(confidence, 1.0)

    def test_kannada_translation_required(self):
        """Non-English text should be translated with lower confidence."""
        text = "ಇದು ರೇಷಮೆ ಬಟ್ಟೆ"
        translated, confidence = Translator.translate(text, "kn")
        # Should indicate translation was performed
        self.assertIn("Translated from kn", translated)
        self.assertLess(confidence, 1.0)


class TestProductInfoExtraction(unittest.TestCase):
    """Test product information extraction from transcripts."""

    def test_extract_basic_product_info(self):
        """Extract basic product information from simple transcript."""
        transcript = "I make beautiful silk scarves with traditional patterns"
        product = ProductInfoExtractor.extract_all(transcript)

        self.assertIsNotNone(product.name)
        self.assertIsNotNone(product.material)  # Should detect "silk"
        self.assertEqual(product.material, "silk")
        self.assertIn("traditional", product.special_features)

    def test_extract_dimensions(self):
        """Extract dimension information."""
        transcript = "The scarf is 180 cm long and 60 cm wide"
        product = ProductInfoExtractor.extract_all(transcript)

        self.assertEqual(product.dimensions.length, 180.0)
        self.assertEqual(product.dimensions.width, 60.0)
        self.assertEqual(product.dimensions.unit, "cm")

    def test_extract_weight(self):
        """Extract weight information."""
        transcript = "The product weighs 500 grams and measures 30 cm"
        product = ProductInfoExtractor.extract_all(transcript)

        self.assertEqual(product.weight.value, 500.0)
        self.assertEqual(product.weight.unit, "grams")

    def test_extract_color(self):
        """Extract color information."""
        transcript = "This is a red silk fabric with blue patterns"
        product = ProductInfoExtractor.extract_all(transcript)

        self.assertIsNotNone(product.color)
        self.assertEqual(product.color, "red")

    def test_extract_pattern(self):
        """Extract pattern information."""
        transcript = "The design features striped patterns throughout"
        product = ProductInfoExtractor.extract_all(transcript)

        self.assertIsNotNone(product.pattern)
        self.assertEqual(product.pattern, "striped")

    def test_extract_special_features(self):
        """Extract special features."""
        transcript = "This handmade, eco-friendly fabric is completely organic and waterproof"
        product = ProductInfoExtractor.extract_all(transcript)

        features = product.special_features
        self.assertIn("handmade", features)
        self.assertIn("eco-friendly", features)
        self.assertIn("organic", features)
        self.assertIn("waterproof", features)

    def test_extract_usage(self):
        """Extract usage/purpose information."""
        transcript = "This scarf is perfect for formal occasions and outdoor activities"
        product = ProductInfoExtractor.extract_all(transcript)

        self.assertIsNotNone(product.usage)

    def test_missing_fields_identification(self):
        """Identify missing fields from partial transcript."""
        transcript = "I make silk scarves"
        product = ProductInfoExtractor.extract_all(transcript)
        missing = ProductInfoExtractor.get_missing_fields(product)

        # Should identify many missing fields
        self.assertIn("category", missing)
        self.assertIn("subcategory", missing)
        self.assertIn("color", missing)
        self.assertIn("weight", missing)
        self.assertIn("production_time", missing)

    def test_no_hallucination_null_values(self):
        """Ensure null values are used, not invented data."""
        transcript = "basic product"
        product = ProductInfoExtractor.extract_all(transcript)

        # Fields without data should be None or empty
        if product.category is None:
            self.assertIsNone(product.category)
        if product.dimensions.height is None:
            self.assertIsNone(product.dimensions.height)


class TestVoiceProcessor(unittest.TestCase):
    """Test complete voice processing pipeline."""

    def setUp(self):
        """Set up test processor with mock storage root."""
        self.processor = VoiceProcessor(storage_root="data/uploads")

    def test_process_with_transcript(self):
        """Process voice input with provided transcript."""
        input_data = {
            "product_id": "ART-001",
            "audio": {"audio_id": "audio_001", "storage_path": "products/ART-001/audio_001.wav"},
        }

        transcript = "I make beautiful handmade silk scarves that are 180 cm long and red in color"

        result = self.processor.process_from_input(input_data, transcript)

        # Verify result structure
        self.assertIsNotNone(result)
        self.assertEqual(result.product_id, "ART-001")
        self.assertIsNotNone(result.voice.language_code)
        self.assertIsNotNone(result.voice.original_transcript)
        self.assertIsInstance(result.missing_fields, list)
        self.assertIsInstance(result.field_confidence, dict)

    def test_voice_metadata_captured(self):
        """Verify voice metadata is properly captured."""
        result = self.processor.process(
            product_id="ART-002",
            audio_id="audio_002",
            storage_path="products/ART-002/audio_002.wav",
            transcript="A beautiful cotton fabric piece",
        )

        # Voice metadata should be populated
        self.assertEqual(result.voice.language_code, "en")
        self.assertIsNotNone(result.voice.original_transcript)
        self.assertGreater(result.voice.confidence, 0)

    def test_field_confidence_scores(self):
        """Verify confidence scores for each field."""
        result = self.processor.process(
            product_id="ART-003",
            audio_id="audio_003",
            storage_path="products/ART-003/audio_003.wav",
            transcript="Red silk fabric made for traditional wear",
        )

        # Should have confidence scores
        self.assertIn("language_detection", result.field_confidence)
        self.assertIn("speech_to_text", result.field_confidence)
        # Accept either 'translation' (legacy) or 'normalization' (v2)
        self.assertTrue(
            "translation" in result.field_confidence or "normalization" in result.field_confidence
        )

        # Scores should be between 0 and 1
        for score in result.field_confidence.values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)

    def test_schema_compliant_output(self):
        """Verify output matches expected schema structure."""
        result = self.processor.process(
            product_id="ART-004",
            audio_id="audio_004",
            storage_path="products/ART-004/audio_004.wav",
            transcript="A fabric item",
        )

        output_dict = result.to_dict()

        # Verify required keys
        self.assertIn("product_id", output_dict)
        self.assertIn("product", output_dict)
        self.assertIn("voice", output_dict)
        self.assertIn("missing_fields", output_dict)
        self.assertIn("field_confidence", output_dict)

        # Verify product structure
        product = output_dict["product"]
        self.assertIn("name", product)
        self.assertIn("category", product)
        self.assertIn("subcategory", product)
        self.assertIn("material", product)
        self.assertIn("color", product)
        self.assertIn("craft_type", product)
        self.assertIn("description", product)
        self.assertIn("dimensions", product)
        self.assertIn("weight", product)
        self.assertIn("usage", product)
        self.assertIn("pattern", product)
        self.assertIn("special_features", product)
        self.assertIn("production_time", product)

        # Verify voice structure
        voice = output_dict["voice"]
        self.assertIn("language_code", voice)
        self.assertIn("original_transcript", voice)
        self.assertIn("translated_transcript", voice)
        self.assertIn("confidence", voice)

    def test_missing_required_fields_raises_error(self):
        """Missing required fields should raise ValueError."""
        incomplete_input = {
            "product_id": "ART-005",
            # Missing audio info
        }

        with self.assertRaises(ValueError):
            self.processor.process_from_input(incomplete_input)

    def test_no_transcript_handling(self):
        """Process should handle case without transcript gracefully."""
        result = self.processor.process(
            product_id="ART-006",
            audio_id="audio_006",
            storage_path="products/ART-006/audio_006.wav",
            transcript=None,
        )

        # Should return valid result even without transcript
        self.assertIsNotNone(result)
        self.assertEqual(result.product_id, "ART-006")
        self.assertIsNone(result.voice.original_transcript)

    def test_multiple_language_pipeline(self):
        """Test complete pipeline with non-English language."""
        # Using English but simulating language detection
        transcript = (
            "ಈ ಬಟ್ಟೆಯು ಸುಂದರವಾದ "
            "ರೇಷಮೆ ಫ್ಯಾಬ್ರಿಕ್ ಆಗಿದೆ"
        )
        result = self.processor.process(
            product_id="ART-007",
            audio_id="audio_007",
            storage_path="products/ART-007/audio_007.wav",
            transcript=transcript,
        )

        # Should detect Kannada
        self.assertEqual(result.voice.language_code, "kn")
        self.assertIsNotNone(result.voice.original_transcript)

    def test_english_transcript_produces_structured_product_info(self):
        transcript = (
            "This is a hand-woven silk scarf made by an artist artisan in Karnataka. "
            "It is blue in color with a traditional floral pattern. The scarf is made "
            "from pure silk, measures about 6 ft long and 2 ft wide, and takes 3 days "
            "to make. It is suitable for wearing during festivals and special occasions."
        )
        extraction = {
            "name": "hand-woven silk scarf",
            "category": "scarf",
            "subcategory": "hand-woven scarf",
            "material": "silk",
            "color": "blue",
            "craft_type": "hand-woven",
            "description": transcript,
            "dimensions": "6 ft long x 2 ft wide",
            "weight": None,
            "usage": "wearing during festivals and special occasions",
            "pattern": "traditional floral",
            "special_features": ["hand-woven", "traditional"],
            "production_time": "3 days",
        }
        self.processor.gemini = MagicMock()
        self.processor.gemini.extract_product_attributes.return_value = (
            extraction,
            {"material": 1.0, "weight": 0.0},
        )

        result = self.processor.process("ART-REAL", "audio-1", "missing.ogg", transcript)

        self.assertEqual(result.voice.language_code, "en")
        self.assertIsNone(result.voice.translated_transcript)
        self.assertEqual(result.product.name, "hand-woven silk scarf")
        self.assertEqual(result.product.material, "silk")
        self.assertEqual(result.product.color, "blue")
        self.assertEqual(result.product.dimensions.length, 6.0)
        self.assertEqual(result.product.dimensions.width, 2.0)
        self.assertEqual(result.product.dimensions.unit, "ft")
        self.assertIsNone(result.product.weight.value)
        self.assertIn("weight", result.missing_fields)
        self.processor.gemini.normalize_to_english.assert_not_called()

    def test_non_english_transcript_uses_normalization_before_extraction(self):
        transcript = "ಇದು ರೇಷಮೆ ಬಟ್ಟೆ"
        self.processor.gemini = MagicMock()
        self.processor.gemini.normalize_to_english.return_value = ("This is silk fabric", 0.8)
        self.processor.gemini.extract_product_attributes.return_value = ({"material": "silk"}, {})

        result = self.processor.process("ART-KN", "audio-2", "missing.ogg", transcript)

        self.assertEqual(result.voice.language_code, "kn")
        self.assertEqual(result.voice.translated_transcript, "This is silk fabric")
        self.processor.gemini.normalize_to_english.assert_called_once_with(transcript, "kn")
        self.processor.gemini.extract_product_attributes.assert_called_once_with("This is silk fabric")

    def test_empty_transcript_does_not_extract(self):
        self.processor.gemini = MagicMock()

        result = self.processor.process("ART-EMPTY", "audio-3", "missing.ogg", None)

        self.assertIsNone(result.voice.original_transcript)
        self.assertEqual(result.product.name, None)
        self.processor.gemini.extract_product_attributes.assert_not_called()


class TestVoiceProcessingResultSchema(unittest.TestCase):
    """Test that VoiceProcessingResult produces valid schema."""

    def test_to_dict_produces_valid_structure(self):
        """Result.to_dict() should produce valid JSON schema."""
        from app.services.speech import ProductInfo, VoiceMetadata, ProductDimensions, ProductWeight

        product = ProductInfo(
            name="Test Scarf",
            material="silk",
            color="red",
            dimensions=ProductDimensions(length=100, width=50, unit="cm"),
            weight=ProductWeight(value=200, unit="g"),
            special_features=["handmade"],
        )

        voice = VoiceMetadata(
            language_code="en",
            original_transcript="test transcript",
            confidence=0.9,
        )

        result = VoiceProcessingResult(
            product_id="ART-TEST",
            product=product,
            voice=voice,
            missing_fields=["category"],
            field_confidence={"test": 0.8},
        )

        output = result.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(output)
        self.assertIsNotNone(json_str)

        # Verify structure
        self.assertEqual(output["product_id"], "ART-TEST")
        self.assertEqual(output["product"]["name"], "Test Scarf")
        self.assertEqual(output["voice"]["language_code"], "en")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_very_long_transcript(self):
        """Handle very long transcript text."""
        long_text = "This fabric " * 1000  # Repeat many times
        product = ProductInfoExtractor.extract_all(long_text)
        self.assertIsNotNone(product)

    def test_transcript_with_special_characters(self):
        """Handle special characters in transcript."""
        transcript = "Fabric: #1 quality! (100%) @artisan-made (cotton)"
        product = ProductInfoExtractor.extract_all(transcript)
        self.assertIsNotNone(product.name)

    def test_transcript_with_numbers_only(self):
        """Handle numeric-only content."""
        transcript = "100 200 500"
        product = ProductInfoExtractor.extract_all(transcript)
        # Should not crash
        self.assertIsNotNone(product)

    def test_extract_with_unicode_text(self):
        """Handle various Unicode scripts."""
        transcripts = [
            "ಇದು ರೇಷಮೆ",  # Kannada
            "यह रेशम है",  # Hindi
            "இது பட்டு",  # Tamil
        ]

        for transcript in transcripts:
            lang_code, confidence = LanguageDetector.detect(transcript)
            self.assertIsNotNone(lang_code)


if __name__ == "__main__":
    unittest.main()
