"""Orchestrator that assembles local image analysis into the shared media shape."""

import logging
from typing import Any
from uuid import uuid4

from .duplicate_detector import DuplicateDetector
from .image_processor import ImageProcessor
from .photo_set_assessor import assess_photo_set
from .quality_analyzer import analyze_pixels
from .shot_classifier import ShotSignals, classify_shot
from .gemini_client import VisionClient
from .primary_image import PrimaryImageProcessor
from .photo_enhancer import PhotoEnhancer, contrast_score
from .quality_decision import decide_photo

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Process a product's image references without requiring a vision API."""

    def __init__(
        self,
        storage_root: str = "data/uploads",
        vision_client: VisionClient | None = None,
        primary_processor: PrimaryImageProcessor | None = None,
    ) -> None:
        self.storage_root = storage_root
        self.vision_client = vision_client
        self.primary_processor = primary_processor

    def process(
        self,
        product_id: str,
        images: list[dict[str, str]],
        signals_by_path: dict[str, ShotSignals] | None = None,
        create_primary: bool = False,
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
        photo_studio = PhotoEnhancer(self.storage_root)
        accepted_count = 0
        enhanced_count = 0
        removed_count = 0
        retake_count = 0
        readiness_issues: list[str] = []
        for image, duplicate_result in zip(images, duplicate_results):
            storage_path = image["storage_path"]
            metadata = ImageProcessor.inspect(image["image_id"], storage_path, self.storage_root)
            pixels, width, height = ImageProcessor.load_grayscale_pixels(storage_path, self.storage_root)
            quality = analyze_pixels(pixels, width, height)
            qualities[storage_path] = quality
            from PIL import Image
            with Image.open(ImageProcessor.resolve_path(storage_path, self.storage_root)) as opened_image:
                before_contrast = contrast_score(opened_image)
            decision = decide_photo(
                quality,
                is_duplicate=duplicate_result.is_duplicate,
                contrast_score=before_contrast,
            )
            final_path = storage_path
            quality_after = quality
            actions = list(decision.actions)
            status = decision.status
            reason = decision.reason
            if status == "enhance":
                candidate_path = f"photo_studio/{uuid4().hex}_enhanced.png"
                photo_studio.enhance(
                    storage_path,
                    candidate_path,
                    brightness_score=quality.brightness_score,
                    contrast=before_contrast,
                    blur_score=quality.blur_score,
                )
                candidate_pixels, candidate_width, candidate_height = ImageProcessor.load_grayscale_pixels(candidate_path, self.storage_root)
                candidate_quality = analyze_pixels(candidate_pixels, candidate_width, candidate_height)
                if candidate_quality.quality_score > quality.quality_score:
                    final_path = candidate_path
                    quality_after = candidate_quality
                    status = "enhanced"
                    enhanced_count += 1
                    accepted_count += 1
                    reason = "Improved lighting, contrast, or sharpness"
                else:
                    ImageProcessor.resolve_path(candidate_path, self.storage_root).unlink(missing_ok=True)
                    status = "kept"
                    actions = []
                    reason = "Enhancement was rejected because it did not improve the image"
                    accepted_count += 1
            elif status == "kept":
                accepted_count += 1
            elif status == "removed":
                removed_count += 1
                readiness_issues.append(reason)
                final_path = None
            else:
                retake_count += 1
                readiness_issues.append(reason)
                final_path = None
            signals = signals_by_path.get(storage_path)
            if signals is None and self.vision_client is not None:
                mime_type = "image/jpeg" if metadata.format in {"jpg", "jpeg"} else f"image/{metadata.format}"
                signals = self.vision_client.analyze_image(
                    ImageProcessor.read_image_bytes(storage_path, self.storage_root), mime_type
                )
                if signals is None:
                    logger.info(
                        "Vision unavailable for image_id=%s storage_path=%s",
                        metadata.image_id,
                        storage_path,
                    )
                else:
                    logger.info(
                        "Vision signals for image_id=%s storage_path=%s: %s",
                        metadata.image_id,
                        storage_path,
                        signals,
                    )
            elif signals is not None:
                logger.info(
                    "Using supplied Vision signals for image_id=%s storage_path=%s: %s",
                    metadata.image_id,
                    storage_path,
                    signals,
                )
            classification = classify_shot(metadata, quality, signals)
            logger.info(
                "Photo classification image_id=%s storage_path=%s type=%s confidence=%.2f explanation=%s",
                metadata.image_id,
                storage_path,
                classification.photo_type,
                classification.confidence,
                classification.explanation,
            )
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
                "original_path": storage_path,
                "final_path": final_path,
                "status": status,
                "quality_score_before": quality.quality_score,
                "quality_score_after": quality_after.quality_score,
                "actions": actions,
                "issues_before": list(quality.issues),
                "reason": reason,
            })

        eligible_paths = {
            item["storage_path"]
            for item in output_images
            if item["status"] in {"kept", "enhanced"}
        }
        assessment = assess_photo_set(
            [
                classification
                for classification in classifications
                if classification.storage_path in eligible_paths
            ],
            {
                path: quality
                for path, quality in qualities.items()
                if path in eligible_paths
            },
            duplicate_paths,
        )
        recommended_primary_path = None
        if create_primary and assessment.recommended_primary:
            if self.primary_processor is None:
                raise ValueError("create_primary requires a primary_processor")
            recommended_primary_path = self.primary_processor.process(assessment.recommended_primary)
        for output_image in output_images:
            output_image["is_recommended_primary"] = output_image["storage_path"] == assessment.recommended_primary

        return {
            "product_id": product_id,
            "media": {
                "images": output_images,
                "available_types": list(assessment.available_types),
                "missing_types": list(assessment.missing_types),
                "media_readiness_score": assessment.media_readiness_score,
                "recommended_primary_path": recommended_primary_path,
                "photo_readiness": {
                    "score": round(
                        (sum(
                            item["quality_score_after"]
                            for item in output_images
                            if item["status"] in {"kept", "enhanced"}
                        ) / accepted_count if accepted_count else 0.0)
                        * (accepted_count / len(images) if images else 0.0),
                        2,
                    ),
                    "total_uploaded": len(images),
                    "accepted": accepted_count,
                    "enhanced": enhanced_count,
                    "removed": removed_count,
                    "needs_retake": retake_count,
                    "issues": readiness_issues,
                },
            },
        }
