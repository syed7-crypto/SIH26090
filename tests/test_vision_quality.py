import tempfile
import unittest
from pathlib import Path

from app.services.vision import ImageProcessor, analyze_pixels


class TestQualityAnalyzer(unittest.TestCase):
    def test_uniform_image_is_flagged_as_blurry(self):
        pixels = [[128.0] * 10 for _ in range(10)]
        result = analyze_pixels(pixels, 10, 10)

        self.assertLess(result.blur_score, 1)
        self.assertIn("likely_blurry", result.issues)

    def test_brightness_and_resolution_are_bounded(self):
        pixels = [[255.0] * 100 for _ in range(100)]
        result = analyze_pixels(pixels, 100, 100)

        self.assertGreaterEqual(result.brightness_score, 0)
        self.assertLessEqual(result.brightness_score, 100)
        self.assertGreaterEqual(result.quality_score, 0)
        self.assertLessEqual(result.quality_score, 100)


class TestImageProcessor(unittest.TestCase):
    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertFalse(ImageProcessor.validate_image_path("../outside.png", directory))

    def test_unsupported_extension_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("not an image", encoding="utf-8")
            self.assertFalse(ImageProcessor.validate_image_path("sample.txt", directory))


if __name__ == "__main__":
    unittest.main()
