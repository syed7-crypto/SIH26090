import io
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.services.speech import (
    ProductInfo,
    VoiceMetadata,
    VoiceProcessingResult,
)


def wav_bytes() -> bytes:
    return b"RIFF" + (36).to_bytes(4, "little") + b"WAVE" + b"fmt " + b"not-real-audio"


def browser_wav_bytes() -> bytes:
    """A valid 48 kHz, stereo PCM WAV matching record_web output."""

    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(48000)
        audio.writeframes((b"\x00\x01\x00\x01") * 4800)
    return output.getvalue()


class TestVoiceAnalysisApi(unittest.TestCase):
    def setUp(self) -> None:
        from app.api.main import app

        self.client = TestClient(app)

    def test_successful_voice_processing_returns_existing_result_shape(self) -> None:
        result = VoiceProcessingResult(
            product_id="ART-001",
            product=ProductInfo(name="Silk scarf", material="silk"),
            voice=VoiceMetadata(
                language_code="en",
                original_transcript="A silk scarf",
                confidence=0.9,
            ),
            missing_fields=["category"],
            field_confidence={"name": 1.0},
        )
        with tempfile.TemporaryDirectory() as root, patch.dict(
            "os.environ", {"STORAGE_ROOT": root}, clear=False
        ), patch("app.api.routes.voice.VoiceProcessor") as processor_class:
            processor_class.return_value.process.return_value = result
            response = self.client.post(
                "/api/v1/products/ART-001/voice/analyze",
                files={"audio": ("recording.wav", wav_bytes(), "audio/wav")},
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["product_id"], "ART-001")
        self.assertEqual(body["product"]["name"], "Silk scarf")
        self.assertEqual(body["voice"]["language_code"], "en")
        self.assertEqual(body["missing_fields"], ["category"])
        processor_class.return_value.process.assert_called_once()
        call = processor_class.return_value.process.call_args.kwargs
        self.assertTrue(call["storage_path"].startswith("voice_analysis/audio-"))
        self.assertNotIn("..", call["storage_path"])

    def test_invalid_file_is_rejected(self) -> None:
        response = self.client.post(
            "/api/v1/products/ART-002/voice/analyze",
            files={"audio": ("recording.wav", b"not audio", "audio/wav")},
        )
        self.assertEqual(response.status_code, 415)

    def test_browser_record_web_wav_is_accepted(self) -> None:
        result = VoiceProcessingResult(
            product_id="ART-005",
            product=ProductInfo(),
            voice=VoiceMetadata(),
        )
        with tempfile.TemporaryDirectory() as root, patch.dict(
            "os.environ", {"STORAGE_ROOT": root}, clear=False
        ), patch("app.api.routes.voice.VoiceProcessor") as processor_class:
            processor_class.return_value.process.return_value = result
            response = self.client.post(
                "/api/v1/products/ART-005/voice/analyze",
                files={"audio": ("artisan_voice.wav", browser_wav_bytes(), "audio/wav")},
            )
            self.assertEqual(response.status_code, 200)
            stored_files = list((Path(root) / "voice_analysis").glob("*.wav"))
            self.assertEqual(len(stored_files), 1)
            self.assertTrue(stored_files[0].read_bytes().startswith(b"RIFF"))

    def test_missing_file_is_rejected(self) -> None:
        response = self.client.post("/api/v1/products/ART-003/voice/analyze")
        self.assertEqual(response.status_code, 422)

    def test_processor_error_is_returned_without_internal_details(self) -> None:
        with tempfile.TemporaryDirectory() as root, patch.dict(
            "os.environ", {"STORAGE_ROOT": root}, clear=False
        ), patch("app.api.routes.voice.VoiceProcessor") as processor_class:
            processor_class.return_value.process.side_effect = RuntimeError("secret path")
            response = self.client.post(
                "/api/v1/products/ART-004/voice/analyze",
                files={"audio": ("recording.wav", wav_bytes(), "audio/wav")},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "Voice processing failed. Please try again.")
        self.assertNotIn("secret path", response.text)


if __name__ == "__main__":
    unittest.main()
