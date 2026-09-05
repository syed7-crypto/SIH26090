"""Language detection from text."""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects language from text using Unicode patterns and heuristics."""

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
        - Unicode character ranges (high confidence: 0.9)
        - Common word presence (medium confidence)
        - Default to English if no other language detected
        """
        if not text or not text.strip():
            return None, 0.0

        detected_languages = {}

        # Check for script/Unicode character ranges (high priority)
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
            ascii_ratio = sum(1 for c in text if ord(c) < 128) / len(text) if text else 0
            if ascii_ratio > 0.7:
                return "en", 0.7
            return "en", 0.4

        # Return language with highest confidence
        best_lang = max(detected_languages.items(), key=lambda x: x[1])
        return best_lang[0], min(best_lang[1], 1.0)
