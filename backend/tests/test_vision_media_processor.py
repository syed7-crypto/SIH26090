import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.vision import MediaProcessor, ShotSignals, validate_media_output
from app.services.vision import PrimaryImageProcessor


class TestMediaProcessor(unittest.TestCase):
    def _write_image(self, root: str, name: str, offset: int) -> str:
        image = Image.new("RGB", (1000, 1000), (30, 30, 30) if offset else (128, 128, 128))
        draw = ImageDraw.Draw(image)
        draw.rectangle((150 + offset, 150, 850 + offset, 850), fill=(220, 220, 220) if offset else (70, 70, 70))
        for position in range(180, 820, 40):
            draw.line((position + offset, 180, position + offset, 820), fill=(210, 210, 210), width=3)
        if offset:
            draw.ellipse((300, 300, 700, 700), outline=(240, 240, 240), width=8)
            draw.rectangle((0, 0, 260, 260), fill=(220, 40, 40))
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
                {primary: ShotSignals(shows_complete_product=True), detail: ShotSignals(close_crop=True)},
            )

            self.assertEqual(result["product_id"], "ART-001")
            validate_media_output(result)
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

    def test_process_can_generate_and_report_clean_primary_path(self):
        class FakeRemover:
            def remove(self, image_bytes: bytes) -> bytes:
                return image_bytes

        with tempfile.TemporaryDirectory() as root:
            source = self._write_image(root, "source.png", 0)
            result = MediaProcessor(
                root,
                primary_processor=PrimaryImageProcessor(root, FakeRemover()),
            ).process(
                "ART-005",
                [{"image_id": "img-5", "storage_path": source}],
                {source: ShotSignals(shows_complete_product=True)},
                create_primary=True,
            )

            self.assertEqual(result["media"]["recommended_primary_path"], "source_primary.png")
            validate_media_output(result)
            self.assertTrue((Path(root) / "source_primary.png").exists())

    def test_contract_validator_rejects_invalid_quality(self):
        with self.assertRaises(ValueError):
            validate_media_output({
                "product_id": "ART-003",
                "media": {
                    "images": [{"image_id": "img", "storage_path": "a.png", "quality_score": 101}],
                    "available_types": [],
                    "missing_types": [],
                    "media_readiness_score": 50,
                },
            })


if __name__ == "__main__":
    unittest.main()
