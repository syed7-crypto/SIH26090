"""Orchestrator that assembles local image analysis into the shared media shape."""

from typing import Any

from .duplicate_detector import DuplicateDetector
from .image_processor import ImageProcessor
from .photo_set_assessor import assess_photo_set
from .quality_analyzer import analyze_pixels
from .shot_classifier import ShotSignals, classify_shot


class MediaProcessor:
    """Process a product's image references without requiring a vision API."""

    def __init__(self, storage_root: str = "data/uploads") -> None:
        self.storage_root = storage_root

    def process(
        self,
        product_id: str,
        images: list[dict[str, str]],
        signals_by_path: dict[str, ShotSignals] | None = None,
    ) -> dict[str, Any]:
        """Return ``product_id`` and a schema-compatible ``media`` fragment.

        Each image requires ``image_id`` and a relative ``storage_path``. The
        optional signal map is intentionally separate so a future model or
        reviewer can provide semantic evidence without changing this API.
        """

        signals_by_path = signals_by_path or {}
        paths = [item["storage_path"] for item in images]
        duplicate_results = DuplicateDetector.find_duplicates(paths, self.storage_root)
        duplicate_paths = {item.storage_path for item in duplicate_results if item.is_duplicate}

        qualities = {}
        classifications = []
        output_images = []
        for image, duplicate_result in zip(images, duplicate_results):
            storage_path = image["storage_path"]
            metadata = ImageProcessor.inspect(image["image_id"], storage_path, self.storage_root)
            pixels, width, height = ImageProcessor.load_grayscale_pixels(storage_path, self.storage_root)
            quality = analyze_pixels(pixels, width, height)
            qualities[storage_path] = quality
            classification = classify_shot(metadata, quality, signals_by_path.get(storage_path))
            classifications.append(classification)
            output_images.append({
                "image_id": metadata.image_id,
                "storage_path": metadata.storage_path,
                "quality_score": quality.quality_score,
                "blur_score": quality.blur_score,
                "brightness_score": quality.brightness_score,
                "is_duplicate": duplicate_result.is_duplicate,
                "photo_type": classification.photo_type,
                "is_recommended_primary": False,
            })

        assessment = assess_photo_set(classifications, qualities, duplicate_paths)
        for output_image in output_images:
            output_image["is_recommended_primary"] = output_image["storage_path"] == assessment.recommended_primary

        return {
            "product_id": product_id,
            "media": {
                "images": output_images,
                "available_types": list(assessment.available_types),
                "missing_types": list(assessment.missing_types),
                "media_readiness_score": assessment.media_readiness_score,
            },
        }

