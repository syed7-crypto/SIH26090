import tempfile
import unittest
from pathlib import Path
from shutil import copyfile
from unittest.mock import patch

from PIL import Image, ImageDraw

from app.services.vision import ImageQuality, MediaProcessor, ShotSignals, validate_media_output
from app.services.vision.photo_enhancer import PhotoEnhancer
from app.services.vision.quality_decision import PhotoDecision, decide_photo


def quality(
    *,
    score=80.0,
    blur=80.0,
    brightness=80.0,
    resolution=100.0,
    visibility=80.0,
    issues=(),
    width=None,
    height=None,
    megapixels=None,
):
    return ImageQuality(
        quality_score=score,
        blur_score=blur,
        brightness_score=brightness,
        resolution_score=resolution,
        framing_score=80.0,
        visibility_score=visibility,
        issues=issues,
        width=width,
        height=height,
        megapixels=megapixels,
    )


def write_test_image(root: str, name: str) -> str:
    image = Image.new("RGB", (1000, 1000), (150, 150, 150))
    draw = ImageDraw.Draw(image)
    draw.rectangle((150, 150, 850, 850), fill=(70, 70, 70))
    image.save(Path(root) / name)
    return name


class TestPhotoDecisions(unittest.TestCase):
    def test_good_image_is_kept(self):
        self.assertEqual(decide_photo(quality(), is_duplicate=False, contrast_score=80).status, "kept")

    def test_dark_but_recoverable_image_is_enhanced(self):
        decision = decide_photo(quality(brightness=40), is_duplicate=False, contrast_score=80)
        self.assertEqual(decision.status, "enhance")
        self.assertIn("brightness_corrected", decision.actions)

    def test_low_contrast_image_is_enhanced(self):
        decision = decide_photo(quality(), is_duplicate=False, contrast_score=40)
        self.assertEqual(decision.status, "enhance")
        self.assertIn("contrast_improved", decision.actions)

    def test_dark_sharp_image_is_an_enhancement_candidate(self):
        decision = decide_photo(
            quality(brightness=30, blur=85),
            is_duplicate=False,
            contrast_score=80,
        )
        self.assertEqual(decision.status, "enhance")


    def test_severely_blurry_image_is_removed(self):
        decision = decide_photo(quality(blur=20), is_duplicate=False, contrast_score=80)
        self.assertEqual(decision.status, "removed")

    def test_duplicate_is_removed(self):
        decision = decide_photo(quality(), is_duplicate=True, contrast_score=80)
        self.assertEqual(decision.status, "removed")
        self.assertIn("Duplicate", decision.reason)

    def test_low_resolution_needs_retake(self):
        decision = decide_photo(
            quality(resolution=30, width=100, height=100, megapixels=0.01),
            is_duplicate=False,
            contrast_score=80,
        )
        self.assertEqual(decision.status, "needs_retake")

    def test_moderate_resolution_is_not_automatically_rejected(self):
        decision = decide_photo(
            quality(resolution=30, width=625, height=591, megapixels=0.37),
            is_duplicate=False,
            contrast_score=80,
        )
        self.assertEqual(decision.status, "kept")

    def test_enhancement_that_improves_quality_is_accepted(self):
        with tempfile.TemporaryDirectory() as root:
            source = write_test_image(root, "improve.png")

            def write_candidate(source_path, output_path, **_kwargs):
                destination = Path(root) / output_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                copyfile(Path(root) / source_path, destination)

            with patch(
                "app.services.vision.media_processor.decide_photo",
                return_value=PhotoDecision(
                    "enhance",
                    "Photo can be improved safely",
                    ("brightness_corrected",),
                ),
            ), patch(
                "app.services.vision.media_processor.analyze_pixels",
                side_effect=[quality(score=50), quality(score=80)],
            ), patch.object(PhotoEnhancer, "enhance", side_effect=write_candidate):
                result = MediaProcessor(root).process(
                    "ART-IMPROVE",
                    [{"image_id": "img-improve", "storage_path": source}],
                )

            image = result["media"]["images"][0]
            self.assertEqual(image["status"], "enhanced")
            self.assertNotEqual(image["final_path"], image["original_path"])

    def test_enhancement_that_worsens_quality_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            source = write_test_image(root, "worsen.png")

            def write_candidate(source_path, output_path, **_kwargs):
                destination = Path(root) / output_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                copyfile(Path(root) / source_path, destination)

            with patch(
                "app.services.vision.media_processor.decide_photo",
                return_value=PhotoDecision(
                    "enhance",
                    "Photo can be improved safely",
                    ("brightness_corrected",),
                ),
            ), patch(
                "app.services.vision.media_processor.analyze_pixels",
                side_effect=[quality(score=80), quality(score=50)],
            ), patch.object(PhotoEnhancer, "enhance", side_effect=write_candidate):
                result = MediaProcessor(root).process(
                    "ART-WORSEN",
                    [{"image_id": "img-worsen", "storage_path": source}],
                )

            image = result["media"]["images"][0]
            self.assertEqual(image["status"], "kept")
            self.assertEqual(image["final_path"], image["original_path"])
            self.assertEqual(image["actions"], [])

    def test_cropped_or_not_visible_needs_retake(self):
        decision = decide_photo(
            quality(visibility=20, issues=("subject_may_be_cropped",)),
            is_duplicate=False,
            contrast_score=80,
        )
        self.assertEqual(decision.status, "needs_retake")


class TestPhotoStudioOutput(unittest.TestCase):
    def _write_image(self, root: str, name: str) -> str:
        image = Image.new("RGB", (1000, 1000), (150, 150, 150))
        draw = ImageDraw.Draw(image)
        draw.rectangle((150, 150, 850, 850), fill=(70, 70, 70))
        image.save(Path(root) / name)
        return name

    def test_enhancement_writes_new_file_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as root:
            source = self._write_image(root, "original.png")
            output = "photo_studio/enhanced.png"
            PhotoEnhancer(root).enhance(
                source,
                output,
                brightness_score=40,
                contrast=40,
                blur_score=50,
            )
            self.assertTrue((Path(root) / output).is_file())
            self.assertTrue((Path(root) / source).is_file())
            self.assertNotEqual(
                (Path(root) / source).read_bytes(),
                (Path(root) / output).read_bytes(),
            )

    def test_media_output_contains_photo_studio_result_and_valid_contract(self):
        with tempfile.TemporaryDirectory() as root:
            source = self._write_image(root, "original.png")

            class Vision:
                def analyze_image(self, image_bytes, mime_type):
                    return ShotSignals(shows_complete_product=True)

            result = MediaProcessor(root, vision_client=Vision()).process(
                "ART-STUDIO",
                [{"image_id": "img-1", "storage_path": source}],
            )
            validate_media_output(result)
            self.assertIn("photo_readiness", result["media"])
            image = result["media"]["images"][0]
            self.assertIn(image["status"], {"kept", "enhanced", "removed", "needs_retake"})
            self.assertIn("original_path", image)
            self.assertIn("final_path", image)

    def test_removed_image_does_not_invoke_vision(self):
        class Vision:
            def __init__(self):
                self.calls = 0

            def analyze_image(self, image_bytes, mime_type):
                self.calls += 1
                return ShotSignals(shows_complete_product=True)

        with tempfile.TemporaryDirectory() as root:
            source = "removed.png"
            Image.new("RGB", (1000, 1000), (128, 128, 128)).save(Path(root) / source)
            vision = Vision()
            result = MediaProcessor(root, vision_client=vision).process(
                "ART-REMOVED",
                [{"image_id": "img-removed", "storage_path": source}],
                signals_by_path={},
            )

            self.assertEqual(vision.calls, 0)
            self.assertEqual(result["media"]["images"][0]["status"], "removed")
            validate_media_output(result)

    def test_needs_retake_image_does_not_invoke_vision(self):
        class Vision:
            def __init__(self):
                self.calls = 0

            def analyze_image(self, image_bytes, mime_type):
                self.calls += 1
                return ShotSignals(shows_complete_product=True)

        with tempfile.TemporaryDirectory() as root:
            source = "low_resolution.png"
            low_resolution = Image.new("RGB", (100, 100), (128, 128, 128))
            low_resolution_draw = ImageDraw.Draw(low_resolution)
            for position in range(10, 90, 10):
                low_resolution_draw.line((position, 10, position, 90), fill=(20, 20, 20), width=2)
            low_resolution.save(Path(root) / source)
            vision = Vision()
            result = MediaProcessor(root, vision_client=vision).process(
                "ART-RETAKE",
                [{"image_id": "img-retake", "storage_path": source}],
                signals_by_path={},
            )

            self.assertEqual(vision.calls, 0)
            self.assertEqual(result["media"]["images"][0]["status"], "needs_retake")
            validate_media_output(result)

    def test_usable_image_can_invoke_vision(self):
        class Vision:
            def __init__(self):
                self.calls = 0

            def analyze_image(self, image_bytes, mime_type):
                self.calls += 1
                return ShotSignals(shows_complete_product=True)

        with tempfile.TemporaryDirectory() as root:
            source = self._write_image(root, "usable.png")
            vision = Vision()
            result = MediaProcessor(root, vision_client=vision).process(
                "ART-USABLE",
                [{"image_id": "img-usable", "storage_path": source}],
                signals_by_path={},
            )

            self.assertEqual(vision.calls, 1)
            self.assertEqual(result["media"]["images"][0]["photo_type"], "primary")

    def test_vision_failure_keeps_a_valid_response(self):
        class Vision:
            def analyze_image(self, image_bytes, mime_type):
                return None

        with tempfile.TemporaryDirectory() as root:
            source = self._write_image(root, "vision_unavailable.png")
            result = MediaProcessor(
                root,
                vision_client=Vision(),
            ).process(
                "ART-NO-VISION",
                [{"image_id": "img-no-vision", "storage_path": source}],
                signals_by_path={},
            )

            validate_media_output(result)
            image = result["media"]["images"][0]
            self.assertEqual(image["photo_type"], "other")
            self.assertEqual(image["is_recommended_primary"], False)


if __name__ == "__main__":
    unittest.main()
