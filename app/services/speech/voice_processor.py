"""Voice & Language Intelligence module for artisan product information extraction.

This module handles:
1. Speech-to-text conversion from audio files
2. Language detection
3. Translation to canonical language (English)
4. Product information extraction from transcripts
5. Missing field identification
6. Confidence scoring
"""

import json
import logging
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional, Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ProductDimensions:
    """Dimensions with unit of measurement."""
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class ProductWeight:
    """Weight with unit of measurement."""
    value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class VoiceMetadata:
    """Voice input metadata and processing results."""
    language_code: Optional[str] = None
    original_transcript: Optional[str] = None
    translated_transcript: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ProductInfo:
    """Extracted product information from voice input."""
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    craft_type: Optional[str] = None
    description: Optional[str] = None
    dimensions: ProductDimensions = field(default_factory=ProductDimensions)
    weight: ProductWeight = field(default_factory=ProductWeight)
    usage: Optional[str] = None
    pattern: Optional[str] = None
    special_features: List[str] = field(default_factory=list)
    production_time: Optional[str] = None


@dataclass
class VoiceProcessingResult:
    """Complete voice processing pipeline result."""
    product_id: str
    product: ProductInfo
    voice: VoiceMetadata
    missing_fields: List[str] = field(default_factory=list)
    field_confidence: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format matching schema."""
        return {
            "product_id": self.product_id,
            "product": asdict(self.product),
            "voice": asdict(self.voice),
            "missing_fields": self.missing_fields,
            "field_confidence": self.field_confidence,
        }


class LanguageDetector:
    """Detects language from text using simple heuristics and patterns."""

    # Common language patterns
    LANGUAGE_PATTERNS = {
        "kn": {
            "name": "Kannada",
            "patterns": [r"[\u0c80-\u0cff]"],  # Kannada Unicode range
            "common_words": ["ನಾನು", "ಆ", "ಯಾ", "ಈ"],
        },
        "hi": {
            "name": "Hindi",
            "patterns": [r"[\u0900-\u097f]"],  # Devanagari Unicode range
            "common_words": ["मैं", "यह", "क्या", "है"],
        },
        "ta": {
            "name": "Tamil",
            "patterns": [r"[\u0b80-\u0bff]"],  # Tamil Unicode range
            "common_words": ["நான்", "இது", "என்ன"],
        },
        "te": {
            "name": "Telugu",
            "patterns": [r"[\u0c00-\u0c7f]"],  # Telugu Unicode range
            "common_words": ["నేను", "ఇది", "ఏమిటి"],
        },
        "ml": {
            "name": "Malayalam",
            "patterns": [r"[\u0d00-\u0d7f]"],  # Malayalam Unicode range
            "common_words": ["ഞാൻ", "ഇത്", "എന്താണ്"],
        },
        "en": {
            "name": "English",
            "patterns": [],
            "common_words": ["the", "is", "are", "a", "an"],
        },
    }

    @staticmethod
    def detect(text: Optional[str]) -> tuple[Optional[str], float]:
        """Detect language from text.
        
        Returns tuple of (language_code, confidence)
        Confidence is based on:
        - Unicode character ranges (high confidence)
        - Common word presence (medium confidence)
        - Default to English if no other language detected
        """
        if not text or not text.strip():
            return None, 0.0

        detected_languages: Dict[str, float] = {}

        # Check for script/Unicode character ranges
        for lang_code, lang_info in LanguageDetector.LANGUAGE_PATTERNS.items():
            if lang_code == "en":
                continue  # Skip English, check last

            for pattern in lang_info["patterns"]:
                if re.search(pattern, text):
                    detected_languages[lang_code] = 0.9
                    break

        # Check common words if no script detected
        if not detected_languages:
            text_lower = text.lower()
            for lang_code, lang_info in LanguageDetector.LANGUAGE_PATTERNS.items():
                if lang_code == "en":
                    continue

                common_count = sum(1 for word in lang_info["common_words"] if word in text)
                if common_count > 0:
                    detected_languages[lang_code] = 0.5 + (0.1 * min(common_count, 3))

        # Default to English if nothing else detected
        if not detected_languages:
            # Check if text is mostly ASCII
            ascii_ratio = sum(1 for c in text if ord(c) < 128) / len(text)
            if ascii_ratio > 0.7:
                return "en", 0.7
            return "en", 0.4

        # Return language with highest confidence
        best_lang = max(detected_languages.items(), key=lambda x: x[1])
        return best_lang[0], min(best_lang[1], 1.0)


class Translator:
    """Handles translation between languages to canonical processing language (English)."""

    # For MVP: simple mapping. In production, use external translation API
    SAMPLE_TRANSLATIONS = {
        "kn": {
            "ನನ್ನ ಮಣಿ": "my bead",
            "ರೇಷಮೆ": "silk",
            "ಕೊನೆಗೆ": "finally",
        },
    }

    @staticmethod
    def translate(text: Optional[str], source_lang: Optional[str]) -> tuple[Optional[str], float]:
        """Translate text to English if needed.
        
        Returns tuple of (translated_text, confidence)
        
        For MVP, returns approximate translation with lower confidence.
        Production implementation would use external API.
        """
        if not text or not source_lang or source_lang == "en":
            return text, 1.0

        # For MVP, log that translation would happen
        logger.info(f"Translation required from {source_lang} to English")
        logger.info("In production, this would call Google Translate API")

        # Simple placeholder: indicate that translation is needed
        # Return original with lower confidence to indicate need for review
        translated = f"[Translated from {source_lang}] {text}"

        return translated, 0.4


class ProductInfoExtractor:
    """Extracts structured product information from transcript text."""

    # Field extraction patterns and keywords
    EXTRACTION_PATTERNS = {
        "name": r"(?:(?:my|this|the)?\s*(?:product|item|craft|piece)[\s:]*)?([a-zA-Z0-9\s\-\.]+?)(?:\s*(?:is|are|made of|has|with)|$)",
        "material": r"(?:(?:made of|material|from|fabric|wood|metal)[\s:]*)?([a-zA-Z\s\-]+?)(?:\s*(?:and|with|has|to|for)|$)",
        "color": r"(?:(?:color|colored|in|painted)[\s:]*)?(\w+(?:\s+\w+)?)(?:\s*(?:and|with|pattern|design)|$)",
        "pattern": r"(?:(?:pattern|design|style)[\s:]*)?([a-zA-Z\s\-]+?)(?:\s*(?:and|with|on|made)|$)",
    }

    # Dimension and weight extraction patterns
    # Match patterns like "180 cm long" or "length: 180 cm"
    DIMENSION_PATTERNS = {
        "length": r"(?:length|long)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+long",
        "width": r"(?:width|wide)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+wide",
        "height": r"(?:height|tall|high)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+(?:tall|high|height)",
        "weight": r"(?:weighs?|weight)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+(?:grams?|g\b|kg|pounds?)",
    }

    @staticmethod
    def extract_dimensions(text: str) -> ProductDimensions:
        """Extract dimension information from text."""
        dimensions = ProductDimensions()

        text_lower = text.lower()

        # Extract length
        length_pattern = ProductInfoExtractor.DIMENSION_PATTERNS["length"]
        length_match = re.search(length_pattern, text_lower)
        if length_match:
            # Handle both regex alternatives (different group positions)
            value_str = length_match.group(1) or length_match.group(3)
            unit = length_match.group(2) or length_match.group(4)
            if value_str:
                dimensions.length = float(value_str)
                dimensions.unit = unit or "cm"

        # Extract width - need to find it in the remaining text after length
        width_pattern = ProductInfoExtractor.DIMENSION_PATTERNS["width"]
        width_match = re.search(width_pattern, text_lower)
        if width_match:
            value_str = width_match.group(1) or width_match.group(3)
            unit = width_match.group(2) or width_match.group(4)
            if value_str:
                dimensions.width = float(value_str)
                if not dimensions.unit:
                    dimensions.unit = unit or "cm"

        # Extract height
        height_pattern = ProductInfoExtractor.DIMENSION_PATTERNS["height"]
        height_match = re.search(height_pattern, text_lower)
        if height_match:
            value_str = height_match.group(1) or height_match.group(3)
            unit = height_match.group(2) or height_match.group(4)
            if value_str:
                dimensions.height = float(value_str)
                if not dimensions.unit:
                    dimensions.unit = unit or "cm"

        return dimensions

    @staticmethod
    def extract_weight(text: str) -> ProductWeight:
        """Extract weight information from text."""
        text_lower = text.lower()
        pattern = ProductInfoExtractor.DIMENSION_PATTERNS["weight"]

        weight_match = re.search(pattern, text_lower)
        if weight_match:
            weight = ProductWeight()
            value_str = weight_match.group(1) or weight_match.group(3)
            unit = weight_match.group(2) or weight_match.group(4)
            if value_str:
                weight.value = float(value_str)
                weight.unit = unit or "g"
                return weight

        return ProductWeight()

    @staticmethod
    def extract_features(text: str) -> List[str]:
        """Extract special features from text."""
        features = []

        # Look for feature keywords
        feature_keywords = [
            "handmade",
            "organic",
            "eco-friendly",
            "natural",
            "traditional",
            "waterproof",
            "washable",
            "durable",
            "lightweight",
            "premium",
            "custom",
        ]

        text_lower = text.lower()
        for keyword in feature_keywords:
            if keyword in text_lower:
                features.append(keyword)

        return features

    @staticmethod
    def extract_all(transcript: str) -> ProductInfo:
        """Extract all product information from transcript."""
        product = ProductInfo()

        if not transcript:
            return product

        text_lower = transcript.lower()

        # Extract name (first meaningful phrase)
        words = transcript.split()[:10]  # First 10 words max
        product.name = " ".join(words) if words else None

        # Extract material
        material_keywords = ["silk", "cotton", "wool", "leather", "wood", "metal", "clay", "ceramic"]
        for keyword in material_keywords:
            if keyword in text_lower:
                product.material = keyword
                break

        # Extract color
        color_keywords = [
            "red",
            "blue",
            "green",
            "yellow",
            "orange",
            "purple",
            "black",
            "white",
            "brown",
            "pink",
        ]
        for keyword in color_keywords:
            if keyword in text_lower:
                product.color = keyword
                break

        # Extract usage/category
        if "for" in text_lower:
            for_idx = text_lower.find("for")
            usage_part = transcript[for_idx + 3 : for_idx + 50]
            product.usage = usage_part.strip().rstrip(".,")

        # Extract dimensions
        product.dimensions = ProductInfoExtractor.extract_dimensions(transcript)

        # Extract weight
        product.weight = ProductInfoExtractor.extract_weight(transcript)

        # Extract pattern
        pattern_keywords = ["striped", "dotted", "checked", "plain", "geometric", "floral"]
        for keyword in pattern_keywords:
            if keyword in text_lower:
                product.pattern = keyword
                break

        # Extract special features
        product.special_features = ProductInfoExtractor.extract_features(transcript)

        # Set description to original transcript
        product.description = transcript

        return product

    @staticmethod
    def get_missing_fields(product: ProductInfo) -> List[str]:
        """Identify fields that were not extracted from transcript."""
        missing = []

        if not product.name:
            missing.append("name")
        if not product.category:
            missing.append("category")
        if not product.subcategory:
            missing.append("subcategory")
        if not product.material:
            missing.append("material")
        if not product.color:
            missing.append("color")
        if not product.craft_type:
            missing.append("craft_type")
        if (
            product.dimensions.length is None
            and product.dimensions.width is None
            and product.dimensions.height is None
        ):
            missing.append("dimensions")
        if product.weight.value is None:
            missing.append("weight")
        if not product.usage:
            missing.append("usage")
        if not product.pattern:
            missing.append("pattern")
        if not product.production_time:
            missing.append("production_time")

        return missing


class AudioProcessor:
    """Handles audio file reading and basic validation."""

    SUPPORTED_FORMATS = [".wav", ".mp3", ".flac", ".ogg"]

    @staticmethod
    def validate_audio_path(storage_path: str, storage_root: str) -> bool:
        """Validate that audio file exists and is supported format."""
        full_path = Path(storage_root) / storage_path

        if not full_path.exists():
            logger.error(f"Audio file not found: {full_path}")
            return False

        if full_path.suffix.lower() not in AudioProcessor.SUPPORTED_FORMATS:
            logger.error(f"Unsupported audio format: {full_path.suffix}")
            return False

        return True

    @staticmethod
    def get_audio_size(storage_path: str, storage_root: str) -> int:
        """Get audio file size in bytes."""
        full_path = Path(storage_root) / storage_path
        try:
            return full_path.stat().st_size
        except OSError:
            return 0


class VoiceProcessor:
    """Main voice processing pipeline orchestrator."""

    def __init__(self, storage_root: str = "data/uploads"):
        """Initialize voice processor.
        
        Args:
            storage_root: Root directory for stored audio files
        """
        self.storage_root = storage_root
        logger.info(f"VoiceProcessor initialized with storage_root: {storage_root}")

    def process(
        self, product_id: str, audio_id: str, storage_path: str, transcript: Optional[str] = None
    ) -> VoiceProcessingResult:
        """Process voice input for a product.
        
        Args:
            product_id: Unique product identifier
            audio_id: Unique audio file identifier
            storage_path: Path to audio file relative to storage_root
            transcript: Optional pre-transcribed text (for testing/demo)
        
        Returns:
            VoiceProcessingResult with all extraction results
        """
        logger.info(f"Processing voice for product {product_id}, audio {audio_id}")

        # Step 1: Validate audio file exists
        if not AudioProcessor.validate_audio_path(storage_path, self.storage_root):
            logger.warning(f"Audio file validation failed: {storage_path}")

        file_size = AudioProcessor.get_audio_size(storage_path, self.storage_root)
        logger.debug(f"Audio file size: {file_size} bytes")

        # Step 2: Speech-to-Text (MVP: use provided transcript or log requirement)
        if not transcript:
            logger.info(
                f"No transcript provided for {audio_id}. "
                "In production, call speech-to-text API (Google Cloud Speech, etc.)"
            )
            original_transcript = None
            speech_confidence = 0.0
        else:
            original_transcript = transcript
            speech_confidence = 0.85  # Typical ASR confidence

        # Step 3: Language Detection
        lang_code, lang_confidence = LanguageDetector.detect(original_transcript)
        logger.info(f"Detected language: {lang_code} (confidence: {lang_confidence:.2f})")

        # Step 4: Translation
        translated_text, translation_confidence = Translator.translate(
            original_transcript, lang_code
        )
        logger.info(
            f"Translation complete (confidence: {translation_confidence:.2f})"
            if translated_text != original_transcript
            else "No translation needed"
        )

        # Step 5: Product Information Extraction
        # Use translated text for extraction if available and different from original
        text_for_extraction = translated_text or original_transcript
        product_info = ProductInfoExtractor.extract_all(text_for_extraction or "")

        # Step 6: Missing Fields Identification
        missing_fields = ProductInfoExtractor.get_missing_fields(product_info)
        logger.info(f"Missing fields: {missing_fields}")

        # Step 7: Build result with confidence scores
        voice_metadata = VoiceMetadata(
            language_code=lang_code,
            original_transcript=original_transcript,
            translated_transcript=translated_text if translated_text != original_transcript else None,
            confidence=min(speech_confidence, 1.0),
        )

        result = VoiceProcessingResult(
            product_id=product_id,
            product=product_info,
            voice=voice_metadata,
            missing_fields=missing_fields,
            field_confidence={
                "language_detection": lang_confidence,
                "speech_to_text": speech_confidence,
                "translation": translation_confidence if translated_text != original_transcript else 1.0,
                "overall": min(
                    [speech_confidence, lang_confidence, translation_confidence], key=abs
                ),
            },
        )

        logger.info(f"Voice processing complete for {product_id}")
        return result

    def process_from_input(
        self, input_data: Dict[str, Any], transcript: Optional[str] = None
    ) -> VoiceProcessingResult:
        """Process voice input from standard input format.
        
        Args:
            input_data: Dictionary with product_id and audio info
            transcript: Optional transcript for MVP/testing
            
        Expected format:
            {
                "product_id": "ART-001",
                "audio": {
                    "audio_id": "audio_001",
                    "storage_path": "products/ART-001/audio_001.wav"
                }
            }
        
        Returns:
            VoiceProcessingResult
        """
        product_id = input_data.get("product_id")
        audio_info = input_data.get("audio", {})
        audio_id = audio_info.get("audio_id")
        storage_path = audio_info.get("storage_path")

        if not product_id or not audio_id or not storage_path:
            raise ValueError("Missing required fields: product_id, audio.audio_id, audio.storage_path")

        return self.process(product_id, audio_id, storage_path, transcript)
