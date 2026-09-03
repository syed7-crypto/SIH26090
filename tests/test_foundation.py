import os
import unittest
from unittest.mock import patch

from app.config.settings import AppSettings, get_settings


class FoundationTest(unittest.TestCase):
    def test_settings_load_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "test",
                "GEMINI_VISION_MODEL": "configured-model",
            },
            clear=False,
        ):
            settings = get_settings()

        self.assertIsInstance(settings, AppSettings)
        self.assertEqual(settings.app_env, "test")
        self.assertEqual(settings.gemini_vision_model, "configured-model")
        self.assertEqual(settings.gemini_speech_key, "")


if __name__ == "__main__":
    unittest.main()

