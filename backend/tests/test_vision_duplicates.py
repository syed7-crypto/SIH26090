import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.vision import DuplicateDetector


class TestDuplicateDetector(unittest.TestCase):
    def _write_image(self, root: str, name: str, variant: int) -> str:
        image = Image.new("RGB", (64, 64), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((8 + variant, 8, 40 + variant, 40), fill="black")
        path = Path(root) / name
        image.save(path)
        return name

    def test_identical_files_are_duplicates_of_first_occurrence(self):
        with tempfile.TemporaryDirectory() as root:
            first = self._write_image(root, "first.png", 0)
            Path(root, "copy.png").write_bytes(Path(root, first).read_bytes())

            results = DuplicateDetector.find_duplicates([first, "copy.png"], root)

            self.assertFalse(results[0].is_duplicate)
            self.assertTrue(results[1].is_duplicate)
            self.assertTrue(results[1].exact_match)
            self.assertEqual(results[1].duplicate_of, first)

    def test_near_identical_images_are_perceptual_duplicates(self):
        with tempfile.TemporaryDirectory() as root:
            first = self._write_image(root, "first.png", 0)
            second = self._write_image(root, "shifted.png", 1)

            results = DuplicateDetector.find_duplicates([first, second], root)

            self.assertFalse(results[0].is_duplicate)
            self.assertTrue(results[1].is_duplicate)
            self.assertFalse(results[1].exact_match)

    def test_different_images_are_not_duplicates(self):
        with tempfile.TemporaryDirectory() as root:
            first = self._write_image(root, "first.png", 0)
            second = self._write_image(root, "different.png", 20)

            results = DuplicateDetector.find_duplicates([first, second], root, hamming_threshold=2)

            self.assertFalse(results[0].is_duplicate)
            self.assertFalse(results[1].is_duplicate)


if __name__ == "__main__":
    unittest.main()
