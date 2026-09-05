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
        response.candidates = [MagicMock()]
        response.candidates[0].content.parts = [MagicMock()]
        response.candidates[0].content.parts[0].audio_transcription.text = (
            "  A handwoven cotton scarf.  "
        )
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
        responses = []
        empty_part_response = MagicMock()
        empty_part_response.candidates = [MagicMock()]
        empty_part_response.candidates[0].content.parts = [MagicMock()]
        empty_part_response.candidates[0].content.parts[0].audio_transcription = None
        responses.append(empty_part_response)

        for transcription_text in (None, "", "[INAUDIBLE]"):
            response = MagicMock()
            response.candidates = [MagicMock()]
            response.candidates[0].content.parts = [MagicMock()]
            response.candidates[0].content.parts[0].audio_transcription.text = transcription_text
            responses.append(response)

        for response in responses:
            with self.subTest(response=response):
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


class TestGeminiClientExtraction(unittest.TestCase):
    def setUp(self) -> None:
        self.client = GeminiClient.__new__(GeminiClient)
        self.client.client = MagicMock()
        self.client.extraction_model = "configured-extraction-model"

    def test_extracts_json_and_uses_transcript_as_prompt_input(self) -> None:
        response = MagicMock()
        response.text = '{"name": "Silk scarf", "material": "silk", "weight": null, "confidence": {"name": 0.2}}'
        self.client.client.models.generate_content.return_value = response

        extracted, confidence = self.client.extract_product_attributes("A blue silk scarf")

        self.assertEqual(extracted, {"name": "Silk scarf", "material": "silk", "weight": None})
        self.assertEqual(confidence["name"], 1.0)
        self.assertEqual(confidence["weight"], 0.0)
        call_kwargs = self.client.client.models.generate_content.call_args.kwargs
        prompt = call_kwargs["contents"]
        self.assertIn("A blue silk scarf", prompt)
        self.assertEqual(call_kwargs["config"].http_options.timeout, 45000)

    def test_extraction_failure_returns_empty_values(self) -> None:
        self.client.client.models.generate_content.side_effect = RuntimeError("API failure")

        extracted, confidence = self.client.extract_product_attributes("A silk scarf")

        self.assertEqual(extracted, {})
        self.assertEqual(confidence, {})

    def test_unavailable_client_returns_empty_values(self) -> None:
        self.client.client = None

        extracted, confidence = self.client.extract_product_attributes("A silk scarf")

        self.assertEqual(extracted, {})
        self.assertEqual(confidence, {})


if __name__ == "__main__":
    unittest.main()
