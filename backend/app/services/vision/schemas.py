"""Data models for local product-media analysis."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ImageMetadata:
    """Safe, provider-independent metadata for one stored image."""

    image_id: str
    storage_path: str
    format: str
    width: int
    height: int
    file_size_bytes: int


@dataclass(frozen=True)
class ImageQuality:
    """Normalized local quality measurements, each score ranging from 0 to 100."""

    quality_score: float
    blur_score: float
    brightness_score: float
    resolution_score: float
    framing_score: float
    visibility_score: Optional[float] = None
    issues: tuple[str, ...] = ()
    width: Optional[int] = None
    height: Optional[int] = None
    megapixels: Optional[float] = None

