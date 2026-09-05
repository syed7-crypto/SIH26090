"""Voice & Language Intelligence module - Gemini-powered orchestrator.

Pipeline:
    Audio File
      ↓
    [AudioProcessor] Validate audio
      ↓
    [GeminiClient] Speech-to-text
      ↓
    [LanguageDetector] Detect language
      ↓
    [GeminiClient] Normalize to English (if needed)
      ↓
    [GeminiClient] Extract product attributes
      ↓
    [Missing Fields] Identify gaps
      ↓
    VoiceProcessingResult
"""

import logging
import re
from typing import Optional, Dict, Any

from .schemas import (
    ProductInfo,
    VoiceMetadata,
    VoiceProcessingResult,
    ProductDimensions,
    ProductWeight,
)
from .audio_processor import AudioProcessor
from .language_detection import LanguageDetector
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Main voice processing pipeline orchestrator using Gemini AI."""

    def __init__(
        self,
        storage_root: str = "data/uploads",
        gemini_api_key: Optional[str] = None,
        speech_model: Optional[str] = None,
        extraction_model: Optional[str] = None,
    ):
        """Initialize voice processor.
        
        Args:
            storage_root: Root directory for stored audio files
            gemini_api_key: Gemini API key (defaults to env var)
            speech_model: Gemini model for STT (defaults to env var)
            extraction_model: Gemini model for extraction (defaults to env var)
        """
        self.storage_root = storage_root
        self.gemini = GeminiClient(
            api_key=gemini_api_key,
            speech_model=speech_model,
            extraction_model=extraction_model,
        )
        logger.info(f"VoiceProcessor initialized with storage_root: {storage_root}")

    def process(
        self,
        product_id: str,
        audio_id: str,
        storage_path: str,
        transcript: Optional[str] = None,
    ) -> VoiceProcessingResult:
        """Process voice input for a product using Gemini AI.
        
        Args:
            product_id: Unique product identifier
            audio_id: Unique audio file identifier
            storage_path: Path to audio file relative to storage_root
            transcript: Optional pre-transcribed text (for testing/backward compat)
        
        Returns:
            VoiceProcessingResult with all extraction results
        """
        logger.info(f"Processing voice for product {product_id}, audio {audio_id}")

        # Step 1: Validate audio file
        audio_valid = AudioProcessor.validate_audio_path(storage_path, self.storage_root)
        file_size = AudioProcessor.get_audio_size(storage_path, self.storage_root)
        logger.debug(f"Audio file validation: {audio_valid}, size: {file_size} bytes")

        # Step 2: Speech-to-Text
        if transcript:
            # Backward compatibility: use provided transcript
            original_transcript = transcript
            speech_confidence = 0.85
            logger.info("Using provided transcript (backward compatibility)")
        else:
            # Use Gemini STT
            try:
                if not audio_valid:
                    logger.warning(f"Audio file validation failed: {storage_path}")
                    original_transcript = None
                    speech_confidence = 0.0
                else:
                    audio_bytes = AudioProcessor.read_audio_bytes(storage_path, self.storage_root)
                    original_transcript, speech_confidence = self.gemini.transcribe_audio(audio_bytes)
                    logger.info(f"Transcription confidence: {speech_confidence:.2f}")
            except Exception as e:
                logger.error(f"Failed to transcribe audio: {e}")
                original_transcript = None
                speech_confidence = 0.0

        # Step 3: Language Detection
        lang_code, lang_confidence = LanguageDetector.detect(original_transcript)
        logger.info(f"Detected language: {lang_code} (confidence: {lang_confidence:.2f})")

        # Step 4: Normalize to English if needed
        if original_transcript and lang_code and lang_code != "en":
            normalized_transcript, normalization_confidence = self.gemini.normalize_to_english(
                original_transcript, lang_code
            )
            logger.info(f"Normalization confidence: {normalization_confidence:.2f}")
        else:
            normalized_transcript = None
            normalization_confidence = 1.0

        # Step 5: Extract Product Attributes using Gemini
        text_for_extraction = normalized_transcript or original_transcript
        
        if text_for_extraction:
            extracted_attrs, field_confidences = self.gemini.extract_product_attributes(
                text_for_extraction
            )
            logger.info(f"Extracted {len(extracted_attrs)} attributes from transcript")
        else:
            extracted_attrs = {}
            field_confidences = {}
            logger.warning("No transcript available for attribute extraction")

        # Step 6: Build ProductInfo from extracted attributes
        product_info = self._build_product_info(extracted_attrs)

        # Step 7: Identify missing fields
        missing_fields = self._identify_missing_fields(product_info)
        logger.info(f"Missing fields: {missing_fields}")

        # Step 8: Build result with confidence scores
        voice_metadata = VoiceMetadata(
            language_code=lang_code,
            original_transcript=original_transcript,
            translated_transcript=normalized_transcript,
            confidence=min(speech_confidence, 1.0),
        )

        # Merge all confidence scores
        all_confidences = {
            "language_detection": lang_confidence,
            "speech_to_text": speech_confidence,
            "normalization": normalization_confidence if normalized_transcript else 1.0,
        }
        all_confidences.update(field_confidences)

        result = VoiceProcessingResult(
            product_id=product_id,
            product=product_info,
            voice=voice_metadata,
            missing_fields=missing_fields,
            field_confidence=all_confidences,
        )

        logger.info(f"Voice processing complete for {product_id}")
        return result

    def process_from_input(
        self, input_data: Dict[str, Any], transcript: Optional[str] = None
    ) -> VoiceProcessingResult:
        """Process voice input from standard input format.
        
        Args:
            input_data: Dictionary with product_id and audio info
            transcript: Optional transcript for testing/backward compatibility
            
        Expected input format:
            {
                "product_id": "ART-001",
                "audio": {
                    "audio_id": "audio_001",
                    "storage_path": "products/ART-001/audio_001.wav"
                }
            }
        
        Returns:
            VoiceProcessingResult
            
        Raises:
            ValueError: If required fields are missing
        """
        product_id = input_data.get("product_id")
        audio_info = input_data.get("audio", {})
        audio_id = audio_info.get("audio_id")
        storage_path = audio_info.get("storage_path")

        if not product_id or not audio_id or not storage_path:
            raise ValueError(
                "Missing required fields: product_id, audio.audio_id, audio.storage_path"
            )

        return self.process(product_id, audio_id, storage_path, transcript)

    @staticmethod
    def _build_product_info(extracted_attrs: Dict[str, Any]) -> ProductInfo:
        """Build ProductInfo from Gemini extraction results.
        
        Args:
            extracted_attrs: Dictionary with extracted attributes
            
        Returns:
            ProductInfo object
        """
        product = ProductInfo()

        # Direct string fields
        for field in ["name", "category", "subcategory", "material", "color", "craft_type", "description", "usage", "pattern", "production_time"]:
            if field in extracted_attrs:
                setattr(product, field, extracted_attrs[field])

        # Parse dimensions if provided
        if extracted_attrs.get("dimensions"):
            dims_str = extracted_attrs["dimensions"]
            length, length_unit = _parse_measurement(dims_str, ("length", "long"))
            width, width_unit = _parse_measurement(dims_str, ("width", "wide"))
            height, height_unit = _parse_measurement(dims_str, ("height", "tall", "high"))
            product.dimensions = ProductDimensions(
                length=length,
                width=width,
                height=height,
                unit=length_unit or width_unit or height_unit,
            )

        # Parse weight if provided
        if extracted_attrs.get("weight"):
            weight_str = extracted_attrs["weight"]
            weight_value = _parse_dimension(weight_str, "weight")
            if weight_value:
                product.weight = ProductWeight(value=weight_value, unit="g")

        # Special features
        if extracted_attrs.get("special_features"):
            features = extracted_attrs["special_features"]
            product.special_features = features if isinstance(features, list) else [features]

        return product

    @staticmethod
    def _identify_missing_fields(product: ProductInfo) -> list[str]:
        """Identify fields that were not extracted.
        
        Args:
            product: ProductInfo object
            
        Returns:
            List of field names that are missing/null
        """
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


def _parse_dimension(text: str, keyword: str) -> Optional[float]:
    """Parse numeric dimension from text.
    
    Args:
        text: Text containing dimension
        keyword: Keyword to search for (e.g., "length", "long")
        
    Returns:
        Float value or None
    """
    import re
    
    if not text or not keyword:
        return None
    
    # Look for pattern like "180 cm" or "180cm"
    pattern = f"{keyword}[\\s:]*(\\d+(?:\\.\\d+)?)"
    match = re.search(pattern, text.lower())
    if match:
        return float(match.group(1))
    
    # Try reverse: look for digit followed by unit
    pattern = f"(\\d+(?:\\.\\d+)?)\\s*(?:cm|m|inch|g|kg).*{keyword}"
    match = re.search(pattern, text.lower())
    if match:
        return float(match.group(1))
    
    return None


def _parse_measurement(text: str, labels: tuple[str, ...]) -> tuple[Optional[float], Optional[str]]:
    """Parse a labeled measurement while preserving its stated unit."""
    if not text:
        return None, None

    label_pattern = "|".join(re.escape(label) for label in labels)
    unit_pattern = r"(?:feet|foot|ft|inches|inch|in|cm|m|meters?|g|kg|grams?|pounds?|lb)"
    patterns = (
        rf"(\d+(?:\.\d+)?)\s*({unit_pattern})\s*(?:{label_pattern})\b",
        rf"(?:{label_pattern})\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*({unit_pattern})\b",
    )

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1)), match.group(2)

    return None, None


# Legacy classes for backward compatibility with existing tests
class Translator:
    """Handles translation between languages to canonical processing language (English).
    
    NOTE: In production, this is replaced by GeminiClient.normalize_to_english()
    """

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

        logger.info(f"Translation required from {source_lang} to English")
        logger.info("In production, this would call Gemini API")

        # Simple placeholder: indicate that translation is needed
        translated = f"[Translated from {source_lang}] {text}"

        return translated, 0.4


class ProductInfoExtractor:
    """Extracts structured product information from transcript text.
    
    NOTE: In production, this is replaced by GeminiClient.extract_product_attributes()
    """

    # Field extraction patterns and keywords
    EXTRACTION_PATTERNS = {
        "name": r"(?:(?:my|this|the)?\s*(?:product|item|craft|piece)[\s:]*)?([a-zA-Z0-9\s\-\.]+?)(?:\s*(?:is|are|made of|has|with)|$)",
        "material": r"(?:(?:made of|material|from|fabric|wood|metal)[\s:]*)?([a-zA-Z\s\-]+?)(?:\s*(?:and|with|has|to|for)|$)",
        "color": r"(?:(?:color|colored|in|painted)[\s:]*)?(\w+(?:\s+\w+)?)(?:\s*(?:and|with|pattern|design)|$)",
        "pattern": r"(?:(?:pattern|design|style)[\s:]*)?([a-zA-Z\s\-]+?)(?:\s*(?:and|with|on|made)|$)",
    }

    # Dimension and weight extraction patterns
    DIMENSION_PATTERNS = {
        "length": r"(?:length|long)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+long",
        "width": r"(?:width|wide)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+wide",
        "height": r"(?:height|tall|high)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+(?:tall|high|height)",
        "weight": r"(?:weighs?|weight)\s+(\d+(?:\.\d+)?)\s+([a-z]+)|(\d+(?:\.\d+)?)\s+([a-z]+)\s+(?:grams?|g\b|kg|pounds?)",
    }

    @staticmethod
    def extract_dimensions(text: str) -> ProductDimensions:
        """Extract dimension information from text."""
        import re
        
        dimensions = ProductDimensions()
        text_lower = text.lower()

        # Extract length
        length_pattern = ProductInfoExtractor.DIMENSION_PATTERNS["length"]
        length_match = re.search(length_pattern, text_lower)
        if length_match:
            value_str = length_match.group(1) or length_match.group(3)
            unit = length_match.group(2) or length_match.group(4)
            if value_str:
                dimensions.length = float(value_str)
                dimensions.unit = unit or "cm"

        # Extract width
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
        import re
        
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
    def extract_features(text: str) -> list:
        """Extract special features from text."""
        features = []

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
        words = transcript.split()[:10]
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

        # Extract usage
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
    def get_missing_fields(product: ProductInfo) -> list:
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
