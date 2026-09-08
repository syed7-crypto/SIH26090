import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.vision import MediaProcessor, ShotSignals, VisionClient


class FakeVisionClient:
    def analyze_image(self, image_bytes: bytes, mime_type: str) -> ShotSignals:
        self.called_with = (image_bytes, mime_type)
        return ShotSignals(has_person=True, is_being_worn_or_used=True)


class TestVisionClient(unittest.TestCase):
    def test_without_key_it_degrades_to_local_processing(self):
        client = VisionClient(api_key=None)
        self.assertIsNone(client.analyze_image(b"not sent", "image/png"))

    def test_media_processor_can_use_injected_vision_client(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "product.png"
            image = Image.new("RGB", (1000, 1000), (128, 128, 128))
            draw = ImageDraw.Draw(image)
            draw.rectangle((150, 150, 850, 850), fill=(70, 70, 70))
            for position in range(180, 820, 40):
                draw.line((position, 180, position, 820), fill=(210, 210, 210), width=3)
            image.save(path)
            fake = FakeVisionClient()
            result = MediaProcessor(root, vision_client=fake).process(
                "ART-004", [{"image_id": "img-4", "storage_path": "product.png"}]
            )

            self.assertEqual(result["media"]["images"][0]["photo_type"], "lifestyle")
            self.assertEqual(fake.called_with[1], "image/png")


if __name__ == "__main__":
    unittest.main()
