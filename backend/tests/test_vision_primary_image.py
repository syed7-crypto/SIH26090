import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.services.vision import PrimaryImageProcessor


class FakeBackgroundRemover:
    def remove(self, image_bytes: bytes) -> bytes:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()


class TestPrimaryImageProcessor(unittest.TestCase):
    def test_creates_separate_primary_image_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "sample.jpg"
            Image.new("RGB", (20, 20), "red").save(source)
            original_bytes = source.read_bytes()

            output_path = PrimaryImageProcessor(root, FakeBackgroundRemover()).process("sample.jpg")

            self.assertEqual(output_path, "sample_primary.png")
            self.assertEqual(source.read_bytes(), original_bytes)
            self.assertTrue((Path(root) / output_path).is_file())
            with Image.open(Path(root) / output_path) as generated:
                self.assertEqual(generated.format, "PNG")

    def test_backend_failure_does_not_create_output(self):
        class FailingRemover:
            def remove(self, image_bytes: bytes) -> bytes:
                raise RuntimeError("segmentation failed")

        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "sample.jpg"
            Image.new("RGB", (20, 20), "red").save(source)
            with self.assertRaisesRegex(RuntimeError, "segmentation failed"):
                PrimaryImageProcessor(root, FailingRemover()).process("sample.jpg")
            self.assertFalse((Path(root) / "sample_primary.png").exists())


if __name__ == "__main__":
    unittest.main()
