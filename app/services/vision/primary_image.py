"""Product-only primary-image generation boundary."""

from pathlib import Path
from typing import Protocol

from .image_processor import ImageProcessor


class BackgroundRemover(Protocol):
    """Backend contract for removing non-product pixels."""

    def remove(self, image_bytes: bytes) -> bytes:
        """Return a PNG-encoded RGBA image with background transparency."""


class RembgBackgroundRemover:
    """Optional local backend powered by the rembg segmentation model."""

    def __init__(self, model_name: str = "u2netp") -> None:
        # u2netp is substantially smaller than rembg's newest default model.
        self.model_name = model_name
        self._session = None

    def remove(self, image_bytes: bytes) -> bytes:
        try:
            from rembg import new_session, remove
        except ImportError as exc:
            raise RuntimeError(
                "Product-only generation requires an installed background-removal backend "
                "such as rembg; the original image was not modified."
            ) from exc
        if self._session is None:
            self._session = new_session(self.model_name)
        return remove(image_bytes, session=self._session)


class PrimaryImageProcessor:
    """Create a separate clean-primary image using an injected remover."""

    def __init__(self, storage_root: str = "data/uploads", remover: BackgroundRemover | None = None) -> None:
        self.storage_root = storage_root
        self.remover = remover or RembgBackgroundRemover()

    def process(self, storage_path: str, output_path: str | None = None) -> str:
        """Remove the background and return the new relative storage path."""

        source = ImageProcessor.resolve_path(storage_path, self.storage_root)
        destination_path = output_path or f"{Path(storage_path).with_suffix('').as_posix()}_primary.png"
        destination = ImageProcessor.resolve_path(destination_path, self.storage_root)
        if source == destination:
            raise ValueError("primary output must not overwrite the original image")
        if not source.is_file():
            raise FileNotFoundError(f"Image file not found: {source}")

        result_bytes = self.remover.remove(source.read_bytes())
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(result_bytes)
        return destination_path.replace("\\", "/")
