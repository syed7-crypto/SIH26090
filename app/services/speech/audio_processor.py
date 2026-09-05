"""Audio file validation and handling."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio file validation and metadata."""

    SUPPORTED_FORMATS = [".wav", ".mp3", ".flac", ".ogg"]

    @staticmethod
    def validate_audio_path(storage_path: str, storage_root: str) -> bool:
        """Validate that audio file exists and is supported format.
        
        Args:
            storage_path: Relative path to audio file
            storage_root: Root directory for audio storage
            
        Returns:
            True if file is valid, False otherwise
        """
        full_path = Path(storage_root) / storage_path

        if not full_path.exists():
            logger.error(f"Audio file not found: {full_path}")
            return False

        if full_path.suffix.lower() not in AudioProcessor.SUPPORTED_FORMATS:
            logger.error(f"Unsupported audio format: {full_path.suffix}")
            return False

        return True

    @staticmethod
    def get_audio_size(storage_path: str, storage_root: str) -> int:
        """Get audio file size in bytes.
        
        Args:
            storage_path: Relative path to audio file
            storage_root: Root directory for audio storage
            
        Returns:
            File size in bytes, or 0 if file not found
        """
        full_path = Path(storage_root) / storage_path
        try:
            return full_path.stat().st_size
        except OSError:
            logger.warning(f"Could not stat file: {full_path}")
            return 0

    @staticmethod
    def read_audio_bytes(storage_path: str, storage_root: str) -> bytes:
        """Read audio file and return bytes.
        
        Args:
            storage_path: Relative path to audio file
            storage_root: Root directory for audio storage
            
        Returns:
            File contents as bytes
            
        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        full_path = Path(storage_root) / storage_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Audio file not found: {full_path}")
            
        return full_path.read_bytes()
