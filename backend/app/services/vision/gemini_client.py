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
        self.model = model or os.getenv("GEMINI_VISION_MODEL", "gemini-3.5-flash-lite")
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

            prompt = """Inspect this artisan product image and return ONLY this strict JSON object.
This is classification of image composition only. Do not identify the product or invent product attributes.

Definitions:
- has_person: true ONLY if a human/person is visibly present.
- is_being_worn_or_used: true ONLY if the product is visibly being worn, held, carried, used, or demonstrated by a person.
- has_lifestyle_context: true ONLY when the image intentionally presents the product in a real-world lifestyle or use environment. Do not mark this true merely because the product is outdoors, on a table, has a background, contains environmental objects, or is not on a white background.
- shows_complete_product: true when the majority or all of the product is visible and it can be understood as a whole.
- close_crop: true when the image intentionally focuses on a close-up/detail such as weave, texture, embroidery, stitching, craftsmanship, or material detail.
- shows_side_or_back: true when the image primarily shows the side, back, bottom, or another alternate structural view.
- has_scale_reference: true ONLY when a meaningful object, person, or reference allows physical size to be understood. Do not infer scale merely because the product is sitting on a table.

Return exactly these boolean fields. Use false unless clearly supported:
{
  \"has_person\": false,
  \"is_being_worn_or_used\": false,
  \"has_lifestyle_context\": false,
  \"shows_complete_product\": true,
  \"close_crop\": false,
  \"shows_side_or_back\": false,
  \"has_scale_reference\": false
}
Do not infer lifestyle context from an ordinary table or outdoor background."""
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
                has_person=bool(values.get("has_person", False)),
                is_being_worn_or_used=bool(values.get("is_being_worn_or_used", False)),
                has_lifestyle_context=bool(values.get("has_lifestyle_context", False)),
                shows_complete_product=bool(values.get("shows_complete_product", False)),
                close_crop=bool(values.get("close_crop", False)),
                shows_side_or_back=bool(values.get("shows_side_or_back", False)),
                has_scale_reference=bool(values.get("has_scale_reference", False)),
            )
        except Exception as exc:
            logger.warning("Gemini Vision analysis failed: %s", exc)
            return None
