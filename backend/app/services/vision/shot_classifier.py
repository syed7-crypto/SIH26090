"""Conservative, provider-independent shot classification."""

from dataclasses import dataclass
from typing import Literal

from .schemas import ImageMetadata, ImageQuality

PhotoType = Literal["primary", "lifestyle", "detail", "side_back", "other"]


@dataclass(frozen=True)
class ShotSignals:
    """Explicit semantic signals supplied by Vision or UI review."""

    has_person: bool = False
    is_being_worn_or_used: bool = False
    has_lifestyle_context: bool = False
    shows_complete_product: bool = False
    close_crop: bool = False
    shows_side_or_back: bool = False
    has_scale_reference: bool = False


@dataclass(frozen=True)
class ShotClassification:
    image_id: str
    storage_path: str
    photo_type: PhotoType
    confidence: float
    explanation: str


def classify_shot(
    metadata: ImageMetadata,
    quality: ImageQuality,
    signals: ShotSignals | None = None,
) -> ShotClassification:
    """Classify a shot using explicit semantic signals and local quality."""

    if signals is None:
        return ShotClassification(
            metadata.image_id,
            metadata.storage_path,
            "other",
            0.0,
            "semantic shot classification unavailable",
        )
    if signals.is_being_worn_or_used:
        return ShotClassification(metadata.image_id, metadata.storage_path, "lifestyle", 0.9, "product is being worn or used")
    if signals.has_lifestyle_context:
        return ShotClassification(metadata.image_id, metadata.storage_path, "lifestyle", 0.85, "product is presented in a lifestyle context")
    if signals.close_crop:
        return ShotClassification(metadata.image_id, metadata.storage_path, "detail", 0.85, "close-crop signal supplied")
    if signals.shows_side_or_back:
        return ShotClassification(metadata.image_id, metadata.storage_path, "side_back", 0.85, "side/back signal supplied")
    visibility_usable = quality.visibility_score is None or quality.visibility_score >= 50
    if signals.shows_complete_product and quality.quality_score >= 60 and visibility_usable:
        return ShotClassification(metadata.image_id, metadata.storage_path, "primary", 0.9, "complete product view with acceptable quality")
    return ShotClassification(metadata.image_id, metadata.storage_path, "other", 0.35, "insufficient evidence for a semantic shot type")
