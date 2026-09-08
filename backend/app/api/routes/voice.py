"""Voice upload and Voice & Language Intelligence API routes."""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config.settings import get_settings
from app.services.speech import AudioProcessor, VoiceProcessor

router = APIRouter(prefix="/api/v1/products", tags=["voice"])

MAX_AUDIO_BYTES = 25 * 1024 * 1024


def _audio_signature_is_valid(audio_bytes: bytes, extension: str) -> bool:
    """Perform a small container check before handing the file to the service."""

    if extension == ".wav":
        return len(audio_bytes) >= 12 and audio_bytes[:4] == b"RIFF" and audio_bytes[8:12] == b"WAVE"
    if extension == ".flac":
        return audio_bytes.startswith(b"fLaC")
    if extension == ".ogg":
        return audio_bytes.startswith(b"OggS")
    if extension == ".mp3":
        return audio_bytes.startswith(b"ID3") or (
            len(audio_bytes) >= 2 and audio_bytes[0] == 0xFF and audio_bytes[1] & 0xE0 == 0xE0
        )
    return False


async def _read_and_validate_audio(upload: UploadFile) -> tuple[bytes, str]:
    filename = upload.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in AudioProcessor.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Supported audio formats are WAV, MP3, FLAC, and OGG.",
        )

    audio_bytes = await upload.read(MAX_AUDIO_BYTES + 1)
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The audio file must be 25 MB or smaller.",
        )
    if not _audio_signature_is_valid(audio_bytes, extension):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The upload is not a valid supported audio file.",
        )
    return audio_bytes, extension


@router.post("/{product_id}/voice/analyze")
async def analyze_product_voice(
    product_id: str,
    audio: UploadFile = File(...),
) -> dict:
    """Store one recording and delegate all processing to VoiceProcessor."""

    audio_bytes, extension = await _read_and_validate_audio(audio)
    settings = get_settings()
    storage_root = Path(settings.storage_root).resolve()
    audio_id = f"audio-{uuid4().hex}"
    relative_path = Path("voice_analysis") / f"{audio_id}{extension}"
    destination = storage_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(audio_bytes)

    try:
        result = VoiceProcessor(
            storage_root=str(storage_root),
            gemini_api_key=settings.gemini_speech_key or None,
            speech_model=settings.gemini_speech_model or None,
            extraction_model=settings.gemini_catalog_model or None,
        ).process(
            product_id=product_id,
            audio_id=audio_id,
            storage_path=relative_path.as_posix(),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Voice processing failed. Please try again.",
        ) from exc

    return result.to_dict()
