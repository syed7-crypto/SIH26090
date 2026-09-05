"""Validation for the media portion of the shared product contract."""

from typing import Any


PHOTO_TYPES = {"primary", "lifestyle", "detail", "side_back", "other"}
REQUIRED_IMAGE_FIELDS = {
    "image_id",
    "storage_path",
    "quality_score",
    "blur_score",
    "brightness_score",
    "is_duplicate",
    "photo_type",
    "is_recommended_primary",
}


def validate_media_output(output: dict[str, Any]) -> None:
    """Raise ``ValueError`` if a media output is not schema-compatible."""

    if not isinstance(output, dict) or not isinstance(output.get("product_id"), str):
        raise ValueError("media output requires a string product_id")
    media = output.get("media")
    if not isinstance(media, dict):
        raise ValueError("media output requires a media object")

    images = media.get("images")
    if not isinstance(images, list):
        raise ValueError("media.images must be an array")
    for image in images:
        missing = REQUIRED_IMAGE_FIELDS - image.keys() if isinstance(image, dict) else REQUIRED_IMAGE_FIELDS
        if missing:
            raise ValueError(f"media image is missing fields: {sorted(missing)}")
        for score_name in ("quality_score", "blur_score", "brightness_score"):
            score = image[score_name]
            if not isinstance(score, (int, float)) or not 0 <= score <= 100:
                raise ValueError(f"{score_name} must be between 0 and 100")
        if not isinstance(image["is_duplicate"], bool) or not isinstance(image["is_recommended_primary"], bool):
            raise ValueError("duplicate and primary flags must be boolean")
        if image["photo_type"] not in PHOTO_TYPES:
            raise ValueError(f"unsupported photo_type: {image['photo_type']}")

    for field in ("available_types", "missing_types"):
        values = media.get(field)
        if not isinstance(values, list) or any(value not in PHOTO_TYPES for value in values):
            raise ValueError(f"media.{field} must contain supported photo types")
    readiness = media.get("media_readiness_score")
    if not isinstance(readiness, (int, float)) or not 0 <= readiness <= 100:
        raise ValueError("media_readiness_score must be between 0 and 100")

