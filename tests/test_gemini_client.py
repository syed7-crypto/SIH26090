import unittest
from unittest.mock import MagicMock

from app.services.speech.gemini_client import GeminiClient


class TestGeminiClientTranscription(unittest.TestCase):
    def setUp(self) -> None:
        self.client = GeminiClient.__new__(GeminiClient)
        self.client.client = MagicMock()
        self.client.speech_model = "configured-speech-model"
        self.client.client.files.upload.return_value = MagicMock(name="uploaded_file")

    def test_successful_transcription_uploads_audio_and_uses_configured_model(self) -> None:
        response = MagicMock()
        response.text = "  A handwoven cotton scarf.  "
        self.client.client.models.generate_content.return_value = response

        transcript, confidence = self.client.transcribe_audio(b"audio bytes", "audio/mpeg")

        self.assertEqual(transcript, "A handwoven cotton scarf.")
        self.assertEqual(confidence, 0.0)
        self.client.client.files.upload.assert_called_once()
        upload_kwargs = self.client.client.files.upload.call_args.kwargs
        self.assertEqual(upload_kwargs["config"].mime_type, "audio/mpeg")
        self.client.client.models.generate_content.assert_called_once_with(
            model="configured-speech-model",
            contents=[self.client.client.files.upload.return_value, unittest.mock.ANY],
        )

    def test_empty_or_inaudible_response_returns_no_transcript(self) -> None:
        for response_text in (None, "", "[INAUDIBLE]"):
            with self.subTest(response_text=response_text):
                response = MagicMock()
                response.text = response_text
                self.client.client.models.generate_content.return_value = response

                transcript, confidence = self.client.transcribe_audio(b"audio bytes")

                self.assertIsNone(transcript)
                self.assertEqual(confidence, 0.0)

    def test_gemini_api_failure_returns_no_transcript(self) -> None:
        self.client.client.models.generate_content.side_effect = RuntimeError("API failure")

        transcript, confidence = self.client.transcribe_audio(b"audio bytes")

        self.assertIsNone(transcript)
        self.assertEqual(confidence, 0.0)

    def test_unavailable_client_returns_no_transcript(self) -> None:
        self.client.client = None

        transcript, confidence = self.client.transcribe_audio(b"audio bytes")

        self.assertIsNone(transcript)
        self.assertEqual(confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
