"""Integration examples for Voice & Language Intelligence module.

This file demonstrates how to use the voice module in practice.
"""

import json
from app.services.speech import VoiceProcessor


def example_1_basic_usage():
    """Example 1: Basic usage with product transcript."""
    print("=" * 60)
    print("Example 1: Basic Voice Processing with Transcript")
    print("=" * 60)

    processor = VoiceProcessor(storage_root="data/uploads")

    # Artisan speaking about their product
    transcript = """
    I make beautiful handmade silk scarves. 
    They are traditionally woven with natural dyes. 
    Each scarf is about 180 cm long and 60 cm wide. 
    The fabric is pure silk in red and gold colors. 
    Each piece takes about 5 days to complete manually. 
    These scarves are perfect for special occasions.
    """

    input_data = {
        "product_id": "ART-001",
        "audio": {"audio_id": "audio_001", "storage_path": "products/ART-001/audio_001.wav"},
    }

    result = processor.process_from_input(input_data, transcript)

    print("\n[PROCESSING COMPLETE]")
    print(json.dumps(result.to_dict(), indent=2))


def example_2_language_detection():
    """Example 2: Language detection with transcript."""
    print("\n" + "=" * 60)
    print("Example 2: Language Support")
    print("=" * 60)

    processor = VoiceProcessor(storage_root="data/uploads")

    transcript = "My beautiful silk fabric made with natural dyes"

    input_data = {
        "product_id": "ART-002",
        "audio": {"audio_id": "audio_002", "storage_path": "products/ART-002/audio_002.wav"},
    }

    result = processor.process_from_input(input_data, transcript)

    print("\n[LANGUAGE DETECTION RESULT]")
    print(f"  Language Code: {result.voice.language_code}")
    print(f"  Detection Confidence: {result.field_confidence.get('language_detection', 0):.2f}")
    print(f"  Original Transcript: {result.voice.original_transcript[:50]}...")
    if result.voice.translated_transcript:
        print(f"  Translation: {result.voice.translated_transcript[:50]}...")


def example_3_partial_information():
    """Example 3: Handling partial information and identifying gaps."""
    print("\n" + "=" * 60)
    print("Example 3: Handling Incomplete Information")
    print("=" * 60)

    processor = VoiceProcessor(storage_root="data/uploads")

    # Minimal transcript - artisan only mentions basic info
    transcript = "I make cotton fabric"

    input_data = {
        "product_id": "ART-003",
        "audio": {"audio_id": "audio_003", "storage_path": "products/ART-003/audio_003.wav"},
    }

    result = processor.process_from_input(input_data, transcript)

    print("\n[EXTRACTED INFORMATION]")
    product = result.product
    print(f"  Name: {product.name}")
    print(f"  Material: {product.material}")
    print(f"  Color: {product.color}")

    print(f"\n[MISSING FIELDS ({len(result.missing_fields)})]")
    for field in result.missing_fields:
        print(f"  - {field}")

    print(f"\n[OVERALL CONFIDENCE SCORE]")
    print(f"  {result.voice.confidence:.2f}")


def example_4_detailed_product():
    """Example 4: Comprehensive product description with all details."""
    print("\n" + "=" * 60)
    print("Example 4: Comprehensive Product Information")
    print("=" * 60)

    processor = VoiceProcessor(storage_root="data/uploads")

    transcript = """
    I am an artisan who creates handmade leather bags.
    These are traditional Indian leather products.
    Each bag is hand-stitched using genuine leather.
    The bags are approximately 40 cm long, 30 cm wide, and 15 cm deep.
    They weigh about 800 grams.
    The leather is naturally dyed in earthy tones - mostly brown and tan.
    We create geometric patterns on the front using traditional stamping techniques.
    These bags are waterproof, durable, and eco-friendly.
    Each piece takes about 3 days to complete.
    They are suitable for daily use, travel, and formal occasions.
    The craft type is traditional hand-stitching with leather work.
    """

    input_data = {
        "product_id": "ART-004",
        "audio": {"audio_id": "audio_004", "storage_path": "products/ART-004/audio_004.wav"},
    }

    result = processor.process_from_input(input_data, transcript)

    output = result.to_dict()

    print("\n[COMPLETE PRODUCT RECORD]")
    print("\nProduct Details:")
    for key, value in output["product"].items():
        if value not in [None, [], {}]:
            print(f"  {key}: {value}")

    print(f"\nVoice Metadata:")
    print(f"  Language: {output['voice']['language_code']}")
    print(f"  Confidence: {output['voice']['confidence']:.2f}")

    if output["missing_fields"]:
        print(f"\nMissing Fields: {output['missing_fields']}")
    else:
        print("\n[ALL KEY FIELDS CAPTURED]")


def example_5_schema_validation():
    """Example 5: Validate output against schema."""
    print("\n" + "=" * 60)
    print("Example 5: Schema Validation")
    print("=" * 60)

    processor = VoiceProcessor(storage_root="data/uploads")

    transcript = "Handwoven cotton sarees with traditional patterns"

    input_data = {
        "product_id": "ART-005",
        "audio": {"audio_id": "audio_005", "storage_path": "products/ART-005/audio_005.wav"},
    }

    result = processor.process_from_input(input_data, transcript)
    output = result.to_dict()

    print("\n[VALIDATING AGAINST SCHEMA]")

    # Check required fields
    required_fields = ["product_id", "product", "voice", "missing_fields", "field_confidence"]
    for field in required_fields:
        status = "OK" if field in output else "MISSING"
        print(f"  {field}: {status}")

    # Check product structure
    print("\n[PRODUCT STRUCTURE]")
    product_fields = [
        "name",
        "category",
        "subcategory",
        "material",
        "color",
        "craft_type",
        "description",
        "dimensions",
        "weight",
        "usage",
        "pattern",
        "special_features",
        "production_time",
    ]
    for field in product_fields:
        status = "OK" if field in output["product"] else "MISSING"
        print(f"  {field}: {status}")

    # Check voice structure
    print("\n[VOICE STRUCTURE]")
    voice_fields = ["language_code", "original_transcript", "translated_transcript", "confidence"]
    for field in voice_fields:
        status = "OK" if field in output["voice"] else "MISSING"
        print(f"  {field}: {status}")

    print("\n[SCHEMA VALIDATION COMPLETE]")


def example_6_field_confidence_tracking():
    """Example 6: Understanding confidence scores."""
    print("\n" + "=" * 60)
    print("Example 6: Field Confidence Tracking")
    print("=" * 60)

    processor = VoiceProcessor(storage_root="data/uploads")

    transcript = "Beautiful blue silk with traditional patterns, 120 cm long"

    input_data = {
        "product_id": "ART-006",
        "audio": {"audio_id": "audio_006", "storage_path": "products/ART-006/audio_006.wav"},
    }

    result = processor.process_from_input(input_data, transcript)

    print("\n[CONFIDENCE SCORES BY COMPONENT]")
    print(f"  Speech-to-Text: {result.field_confidence.get('speech_to_text', 0):.2f}")
    print(f"  Language Detection: {result.field_confidence.get('language_detection', 0):.2f}")
    print(f"  Translation: {result.field_confidence.get('translation', 0):.2f}")
    print(f"  Overall: {result.field_confidence.get('overall', 0):.2f}")

    print("\n[EXTRACTED DATA QUALITY]")
    product = result.product
    print(f"  Material extracted: {product.material is not None}")
    print(f"  Color extracted: {product.color is not None}")
    print(f"  Dimensions extracted: {product.dimensions.length is not None}")
    print(f"  Pattern detected: {len(product.special_features) > 0}")


if __name__ == "__main__":
    # Run all examples
    example_1_basic_usage()
    example_2_language_detection()
    example_3_partial_information()
    example_4_detailed_product()
    example_5_schema_validation()
    example_6_field_confidence_tracking()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)

