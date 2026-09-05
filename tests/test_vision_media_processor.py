import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.vision import MediaProcessor, ShotSignals


class TestMediaProcessor(unittest.TestCase):
    def _write_image(self, root: str, name: str, offset: int) -> str:
        image = Image.new("RGB", (200, 200), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((30 + offset, 30, 150 + offset, 150), fill="black")
        image.save(Path(root) / name)
        return name

    def test_process_returns_shared_media_fragment(self):
        with tempfile.TemporaryDirectory() as root:
            primary = self._write_image(root, "primary.png", 0)
            detail = self._write_image(root, "detail.png", 1)
            result = MediaProcessor(root).process(
                "ART-001",
                [
                    {"image_id": "img-1", "storage_path": primary},
                    {"image_id": "img-2", "storage_path": detail},
                ],
                {detail: ShotSignals(close_crop=True)},
            )

            self.assertEqual(result["product_id"], "ART-001")
            media = result["media"]
            self.assertEqual(len(media["images"]), 2)
            self.assertIn("primary", media["available_types"])
            self.assertIn("detail", media["available_types"])
            self.assertEqual(sum(item["is_recommended_primary"] for item in media["images"]), 1)

    def test_process_marks_exact_duplicate(self):
        with tempfile.TemporaryDirectory() as root:
            first = self._write_image(root, "first.png", 0)
            Path(root, "copy.png").write_bytes(Path(root, first).read_bytes())
            result = MediaProcessor(root).process(
                "ART-002",
                [
                    {"image_id": "img-1", "storage_path": first},
                    {"image_id": "img-2", "storage_path": "copy.png"},
                ],
            )

            self.assertFalse(result["media"]["images"][0]["is_duplicate"])
            self.assertTrue(result["media"]["images"][1]["is_duplicate"])


if __name__ == "__main__":
    unittest.main()
