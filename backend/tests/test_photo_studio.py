import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.vision import ImageQuality, MediaProcessor, ShotSignals, validate_media_output
from app.services.vision.photo_enhancer import PhotoEnhancer
from app.services.vision.quality_decision import decide_photo


def quality(
    *,
    blur=80.0,
    brightness=80.0,
    resolution=100.0,
    visibility=80.0,
    issues=(),
):
    return ImageQuality(
        quality_score=80.0,
        blur_score=blur,
        brightness_score=brightness,
        resolution_score=resolution,
        framing_score=80.0,
        visibility_score=visibility,
        issues=issues,
    )


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

    def test_severely_blurry_image_is_removed(self):
        decision = decide_photo(quality(blur=20), is_duplicate=False, contrast_score=80)
        self.assertEqual(decision.status, "removed")

    def test_duplicate_is_removed(self):
        decision = decide_photo(quality(), is_duplicate=True, contrast_score=80)
        self.assertEqual(decision.status, "removed")
        self.assertIn("Duplicate", decision.reason)

    def test_low_resolution_needs_retake(self):
        decision = decide_photo(quality(resolution=30), is_duplicate=False, contrast_score=80)
        self.assertEqual(decision.status, "needs_retake")

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


if __name__ == "__main__":
    unittest.main()
