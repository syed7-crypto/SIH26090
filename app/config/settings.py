"""Environment-backed application settings.

Secrets are intentionally read from the process environment and are never
stored in source code. A future deployment may provide these variables via a
secret manager or environment file outside version control.
"""

from dataclasses import dataclass
import os


def _env(name: str, default: str = "") -> str:
    """Return an environment variable or its safe, non-secret default."""

    return os.getenv(name, default)


@dataclass(frozen=True)
class AppSettings:
    """Settings shared by application modules."""

    app_env: str = "development"
    log_level: str = "INFO"
    storage_root: str = "data/uploads"

    gemini_vision_key: str = ""
    gemini_speech_key: str = ""
    gemini_catalog_key: str = ""
    gemini_pricing_key: str = ""

    gemini_vision_model: str = ""
    gemini_speech_model: str = ""
    gemini_catalog_model: str = ""
    gemini_pricing_model: str = ""


def get_settings() -> AppSettings:
    """Build settings from environment variables.

    Empty API keys and model names are valid during repository setup; the
    corresponding service should validate its configuration when implemented.
    """

    return AppSettings(
        app_env=_env("APP_ENV", "development"),
        log_level=_env("LOG_LEVEL", "INFO"),
        storage_root=_env("STORAGE_ROOT", "data/uploads"),
        gemini_vision_key=_env("GEMINI_VISION_KEY"),
        gemini_speech_key=_env("GEMINI_SPEECH_KEY"),
        gemini_catalog_key=_env("GEMINI_CATALOG_KEY"),
        gemini_pricing_key=_env("GEMINI_PRICING_KEY"),
        gemini_vision_model=_env("GEMINI_VISION_MODEL"),
        gemini_speech_model=_env("GEMINI_SPEECH_MODEL"),
        gemini_catalog_model=_env("GEMINI_CATALOG_MODEL"),
        gemini_pricing_model=_env("GEMINI_PRICING_MODEL"),
    )

