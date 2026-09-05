"""Conservative, provider-independent shot classification."""

from dataclasses import dataclass
from typing import Literal

from .schemas import ImageMetadata, ImageQuality

PhotoType = Literal["primary", "lifestyle", "detail", "side_back", "other"]


@dataclass(frozen=True)
class ShotSignals:
    """Optional signals supplied by a future vision provider or UI review."""

    has_person_or_context: bool = False
    has_scale_reference: bool = False
    close_crop: bool = False
    shows_side_or_back: bool = False


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
    """Classify a shot using explicit signals, falling back conservatively.

    Without semantic signals, the highest-quality usable image is treated as a
    catalogue/primary candidate. Other images remain ``other`` until a vision
    provider or human review supplies stronger evidence.
    """

    signals = signals or ShotSignals()
    if signals.has_person_or_context:
        return ShotClassification(metadata.image_id, metadata.storage_path, "lifestyle", 0.9, "context/person signal supplied")
    if signals.close_crop:
        return ShotClassification(metadata.image_id, metadata.storage_path, "detail", 0.85, "close-crop signal supplied")
    if signals.shows_side_or_back or signals.has_scale_reference:
        return ShotClassification(metadata.image_id, metadata.storage_path, "side_back", 0.85, "side/back or scale signal supplied")
    visibility_usable = quality.visibility_score is None or quality.visibility_score >= 50
    if quality.quality_score >= 60 and visibility_usable:
        return ShotClassification(metadata.image_id, metadata.storage_path, "primary", 0.55, "usable catalogue candidate; no semantic signal supplied")
    return ShotClassification(metadata.image_id, metadata.storage_path, "other", 0.35, "insufficient evidence for a semantic shot type")
