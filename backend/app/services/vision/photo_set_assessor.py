"""Aggregate image analysis into a product photo-set assessment."""

from dataclasses import dataclass

from .schemas import ImageQuality
from .shot_classifier import ShotClassification, PhotoType


@dataclass(frozen=True)
class PhotoSetAssessment:
    available_types: tuple[PhotoType, ...]
    missing_types: tuple[PhotoType, ...]
    media_readiness_score: float
    recommended_primary: str | None
    issues: tuple[str, ...]


RECOMMENDED_TYPES: tuple[PhotoType, ...] = ("primary", "lifestyle", "detail", "side_back")


def assess_photo_set(
    classifications: list[ShotClassification],
    qualities: dict[str, ImageQuality],
    duplicate_paths: set[str] | None = None,
) -> PhotoSetAssessment:
    """Score coverage and quality with explicit, inspectable rules."""

    duplicate_paths = duplicate_paths or set()
    available = tuple(kind for kind in RECOMMENDED_TYPES if any(item.photo_type == kind for item in classifications))
    missing = tuple(kind for kind in RECOMMENDED_TYPES if kind not in available)
    usable = [
        item
        for item in classifications
        if item.photo_type == "primary"
        and item.storage_path not in duplicate_paths
        and item.storage_path in qualities
    ]
    recommended = max(usable, key=lambda item: qualities[item.storage_path].quality_score, default=None)

    coverage_score = 100.0 * len(available) / len(RECOMMENDED_TYPES)
    quality_score = sum(qualities[item.storage_path].quality_score for item in usable) / len(usable) if usable else 0.0
    duplicate_score = 100.0 if classifications and not duplicate_paths else (50.0 if classifications else 0.0)
    readiness = round(0.4 * coverage_score + 0.4 * quality_score + 0.2 * duplicate_score, 2)

    issues = [f"missing_{kind}" for kind in missing]
    if duplicate_paths:
        issues.append("duplicate_images_present")
    if not usable:
        issues.append("no_usable_images")
    return PhotoSetAssessment(
        available_types=available,
        missing_types=missing,
        media_readiness_score=readiness,
        recommended_primary=recommended.storage_path if recommended else None,
        issues=tuple(issues),
    )

