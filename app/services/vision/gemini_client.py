"""Optional Gemini Vision adapter for semantic image signals."""

import json
import logging
import os
from typing import Any

from .shot_classifier import ShotSignals

logger = logging.getLogger(__name__)


class VisionClient:
    """Small provider adapter; local analysis remains usable without it."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_VISION_KEY")
        self.model = model or os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                logger.warning("Gemini Vision client unavailable: %s", exc)

    def analyze_image(self, image_bytes: bytes, mime_type: str) -> ShotSignals | None:
        """Ask Gemini for explicit semantic signals, returning None on failure."""

        if not self.client:
            return None
        try:
            from google.genai import types

            prompt = """Inspect this artisan product image and return ONLY valid JSON.
Use true only when clearly supported by the image; otherwise use false.
{
  \"has_person_or_context\": boolean,
  \"has_scale_reference\": boolean,
  \"close_crop\": boolean,
  \"shows_side_or_back\": boolean
}
Do not identify the product or invent details."""
            part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            response = self.client.models.generate_content(
                model=self.model,
                contents=[part, prompt],
                config=types.GenerateContentConfig(http_options=types.HttpOptions(timeout=30000)),
            )
            text = response.text.strip() if response.text else "{}"
            if text.startswith("```"):
                text = text.strip("`").removeprefix("json").strip()
            values: dict[str, Any] = json.loads(text)
            return ShotSignals(
                has_person_or_context=bool(values.get("has_person_or_context", False)),
                has_scale_reference=bool(values.get("has_scale_reference", False)),
                close_crop=bool(values.get("close_crop", False)),
                shows_side_or_back=bool(values.get("shows_side_or_back", False)),
            )
        except Exception as exc:
            logger.warning("Gemini Vision analysis failed: %s", exc)
            return None

