"""Product Media Intelligence service."""

from .image_processor import ImageProcessor
from .media_processor import MediaProcessor
from .duplicate_detector import DuplicateDetector, DuplicateResult
from .photo_set_assessor import PhotoSetAssessment, assess_photo_set
from .quality_analyzer import analyze_pixels
from .schemas import ImageMetadata, ImageQuality
from .shot_classifier import ShotClassification, ShotSignals, classify_shot

__all__ = [
    "ImageProcessor",
    "MediaProcessor",
    "ImageMetadata",
    "ImageQuality",
    "DuplicateDetector",
    "DuplicateResult",
    "ShotClassification",
    "ShotSignals",
    "PhotoSetAssessment",
    "classify_shot",
    "assess_photo_set",
    "analyze_pixels",
]
