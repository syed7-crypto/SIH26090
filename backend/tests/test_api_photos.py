import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image


def image_bytes(image_format: str = "PNG", color: str = "red") -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (80, 80), color).save(output, format=image_format)
    return output.getvalue()


class TestPhotoAnalysisApi(unittest.TestCase):
    def setUp(self) -> None:
        from app.api.main import app

        self.client = TestClient(app)

    def request(self, count: int, storage_root: str | None = None):
        files = [
            ("photos", (f"client-name-{index}.png", image_bytes(color=f"#{index + 1:02x}0000"), "image/png"))
            for index in range(count)
        ]
        environment = {"STORAGE_ROOT": storage_root} if storage_root else {}
        return patch.dict("os.environ", environment, clear=False), files

    def test_valid_two_image_upload_returns_media_shape_and_safe_paths(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            environment, files = self.request(2, root)
            with environment:
                response = self.client.post("/api/v1/products/ART-001/photos/analyze", files=files)

            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(body["product_id"], "ART-001")
            self.assertIn("media", body)
            self.assertEqual(len(body["media"]["images"]), 2)
            for image in body["media"]["images"]:
                path = image["storage_path"]
                self.assertFalse(Path(path).is_absolute())
                self.assertNotIn("..", Path(path).parts)
                self.assertTrue((Path(root) / path).is_file())

    def test_valid_five_image_upload_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            environment, files = self.request(5, root)
            with environment:
                response = self.client.post("/api/v1/products/ART-002/photos/analyze", files=files)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()["media"]["images"]), 5)

    def test_fewer_than_two_images_is_rejected(self) -> None:
        response = self.client.post(
            "/api/v1/products/ART-003/photos/analyze",
            files=[("photos", ("one.png", image_bytes(), "image/png"))],
        )
        self.assertEqual(response.status_code, 422)

    def test_more_than_five_images_is_rejected(self) -> None:
        files = [("photos", (f"{index}.png", image_bytes(), "image/png")) for index in range(6)]
        response = self.client.post("/api/v1/products/ART-004/photos/analyze", files=files)
        self.assertEqual(response.status_code, 422)

    def test_unsupported_file_type_is_rejected(self) -> None:
        files = [
            ("photos", ("one.gif", b"GIF89a", "image/gif")),
            ("photos", ("two.png", image_bytes(), "image/png")),
        ]
        response = self.client.post("/api/v1/products/ART-005/photos/analyze", files=files)
        self.assertEqual(response.status_code, 415)

    def test_non_image_file_is_rejected(self) -> None:
        files = [
            ("photos", ("one.png", b"not an image", "image/png")),
            ("photos", ("two.png", image_bytes(), "image/png")),
        ]
        response = self.client.post("/api/v1/products/ART-006/photos/analyze", files=files)
        self.assertEqual(response.status_code, 415)

    def test_supported_image_formats_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            files = [
                ("photos", ("one.jpg", image_bytes("JPEG"), "image/jpeg")),
                ("photos", ("two.webp", image_bytes("WEBP", "blue"), "image/webp")),
            ]
            with patch.dict("os.environ", {"STORAGE_ROOT": root}, clear=False):
                response = self.client.post("/api/v1/products/ART-007/photos/analyze", files=files)
            self.assertEqual(response.status_code, 200)

    def test_provider_can_be_mocked_without_a_real_key(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            files = [
                ("photos", ("one.png", image_bytes(), "image/png")),
                ("photos", ("two.png", image_bytes("PNG", "blue"), "image/png")),
            ]
            with patch.dict("os.environ", {"STORAGE_ROOT": root}, clear=False), patch(
                "app.api.routes.photos.VisionClient"
            ) as vision_client:
                response = self.client.post("/api/v1/products/ART-008/photos/analyze", files=files)

            self.assertEqual(response.status_code, 200)
            vision_client.assert_called_once()

    def test_development_cors_allows_flutter_origin_only(self) -> None:
        response = self.client.options(
            "/api/v1/products/ART-001/photos/analyze",
            headers={
                "Origin": "http://localhost:54874",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:54874",
        )

        rejected = self.client.options(
            "/api/v1/products/ART-001/photos/analyze",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertNotIn("access-control-allow-origin", rejected.headers)


if __name__ == "__main__":
    unittest.main()
