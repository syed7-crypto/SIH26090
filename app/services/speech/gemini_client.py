"""Gemini API client wrapper for speech, translation, and extraction."""

import logging
import io
import os
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Gemini API operations."""

    def __init__(self, api_key: Optional[str] = None, speech_model: Optional[str] = None,
                 extraction_model: Optional[str] = None):
        """Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_SPEECH_KEY or GEMINI_CATALOG_KEY env var)
            speech_model: Model for speech-to-text (defaults to GEMINI_SPEECH_MODEL env var)
            extraction_model: Model for attribute extraction (defaults to GEMINI_CATALOG_MODEL env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_SPEECH_KEY") or os.getenv("GEMINI_CATALOG_KEY")
        self.speech_model = speech_model or os.getenv("GEMINI_SPEECH_MODEL", "gemini-2.0-flash")
        self.extraction_model = extraction_model or os.getenv("GEMINI_CATALOG_MODEL", "gemini-2.0-flash")
        
        if not self.api_key:
            logger.warning("No Gemini API key configured. Set GEMINI_SPEECH_KEY or GEMINI_CATALOG_KEY.")
            self.client = None
        else:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini client initialized. Speech model: {self.speech_model}, Extraction model: {self.extraction_model}")
            except ImportError:
                logger.error("google-genai not installed. Install with: pip install google-genai")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> tuple[Optional[str], float]:
        """Transcribe audio using Gemini speech-to-text.
        
        Args:
            audio_bytes: Raw audio file bytes
            mime_type: MIME type of audio (default: audio/wav)
            
        Returns:
            Tuple of (transcript, confidence)
            - transcript: Transcribed text or None if failed
            - confidence: Confidence score (0.0-1.0)
        """
        if not self.client:
            logger.error("Gemini client not initialized. Cannot transcribe audio.")
            return None, 0.0

        try:
            from google.genai import types
            
            logger.debug(f"Uploading audio ({len(audio_bytes)} bytes) to Gemini Files API")
            file_obj = self.client.files.upload(
                file=io.BytesIO(audio_bytes),
                config=types.UploadFileConfig(mime_type=mime_type),
            )
            
            # Call Gemini for transcription
            prompt = """Transcribe the speech in this audio file exactly as spoken.
            
Return ONLY the transcribed text, without any additional commentary or formatting.
If you cannot understand the speech, return only: [INAUDIBLE]"""
            
            response = self.client.models.generate_content(
                model=self.speech_model,
                contents=[file_obj, prompt],
            )
            
            transcript = response.text.strip() if response.text else None
            
            if not transcript or transcript == "[INAUDIBLE]":
                logger.warning("Audio transcription failed or audio was inaudible")
                return None, 0.0
            
            logger.info(f"Successfully transcribed audio: {len(transcript)} characters")
            # Gemini's generate_content response does not provide STT confidence.
            return transcript, 0.0
            
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}")
            return None, 0.0

    def extract_product_attributes(self, transcript: str) -> tuple[Dict[str, Any], Dict[str, float]]:
        """Extract structured product attributes from transcript using Gemini.
        
        Args:
            transcript: English transcript of artisan describing their product
            
        Returns:
            Tuple of (attributes_dict, confidence_scores)
            - attributes_dict: Extracted product information
            - confidence_scores: Per-field confidence (0.0-1.0)
        """
        if not self.client:
            logger.error("Gemini client not initialized. Cannot extract attributes.")
            return {}, {}

        try:
            import google.genai
            import json
            
            prompt = """You are an expert at extracting product information from artisan descriptions.
            
From the artisan's description below, extract the following product attributes in JSON format.
IMPORTANT: Only extract information explicitly mentioned. Do NOT invent or assume missing details.
For missing fields, use null values.

Return ONLY a valid JSON object (no markdown, no extra text) with this structure:
{
    "name": "product name or null",
    "category": "product category or null",
    "subcategory": "product subcategory or null",
    "material": "primary material or null",
    "color": "color or null",
    "craft_type": "type of craft or null",
    "description": "product description or null",
    "dimensions": "dimensions as string or null",
    "weight": "weight as string or null",
    "usage": "product usage or null",
    "pattern": "pattern or design or null",
    "special_features": ["list", "of", "features"] or [],
    "production_time": "time to produce or null",
    "confidence": {
        "name": 0.0 to 1.0,
        "category": 0.0 to 1.0,
        "material": 0.0 to 1.0,
        "color": 0.0 to 1.0,
        "craft_type": 0.0 to 1.0,
        "description": 0.0 to 1.0,
        "dimensions": 0.0 to 1.0,
        "weight": 0.0 to 1.0,
        "usage": 0.0 to 1.0,
        "pattern": 0.0 to 1.0,
        "special_features": 0.0 to 1.0,
        "production_time": 0.0 to 1.0
    }
}

Artisan description:
{transcript}"""

            logger.debug(f"Sending transcript ({len(transcript)} chars) to Gemini for extraction")
            
            response = self.client.models.generate_content(
                model=self.extraction_model,
                contents=prompt
            )
            
            response_text = response.text.strip() if response.text else "{}"
            
            # Parse JSON response
            extracted = json.loads(response_text)
            
            # Extract confidence scores
            confidence_scores = extracted.pop("confidence", {})
            
            logger.info(f"Successfully extracted {len(extracted)} product attributes")
            return extracted, confidence_scores
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini extraction response as JSON: {e}")
            return {}, {}
        except Exception as e:
            logger.error(f"Error during attribute extraction: {e}")
            return {}, {}

    def normalize_to_english(self, text: str, source_language: str) -> tuple[Optional[str], float]:
        """Normalize text to English if needed.
        
        Args:
            text: Text to normalize
            source_language: Language code (e.g., 'kn' for Kannada)
            
        Returns:
            Tuple of (normalized_text, confidence)
        """
        if source_language == "en" or not source_language:
            return text, 1.0

        if not self.client:
            logger.error("Gemini client not initialized. Cannot normalize text.")
            return text, 0.0

        try:
            import google.genai
            
            prompt = f"""Translate this {source_language.upper()} text to English. 
Return ONLY the English translation, no additional text.

Original text:
{text}"""

            logger.debug(f"Normalizing {source_language} text to English")
            
            response = self.client.models.generate_content(
                model=self.extraction_model,
                contents=prompt
            )
            
            normalized = response.text.strip() if response.text else text
            confidence = 0.80  # Translation confidence
            
            logger.info(f"Successfully normalized text to English")
            return normalized, confidence
            
        except Exception as e:
            logger.warning(f"Failed to normalize text to English: {e}. Using original.")
            return text, 0.5
