"""Image storage and decoding helpers for Product Media Intelligence."""

from pathlib import Path
from .schemas import ImageMetadata


class ImageProcessor:
    """Validate stored image references and expose decoded pixel data."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

    @staticmethod
    def resolve_path(storage_path: str, storage_root: str) -> Path:
        """Resolve a relative storage reference without allowing path traversal."""

        root = Path(storage_root).resolve()
        candidate = (root / storage_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("storage_path must remain inside storage_root") from exc
        return candidate

    @classmethod
    def validate_image_path(cls, storage_path: str, storage_root: str) -> bool:
        """Return whether a stored path points to a supported regular image file."""

        try:
            path = cls.resolve_path(storage_path, storage_root)
        except (TypeError, ValueError):
            return False
        return path.is_file() and path.suffix.lower() in cls.SUPPORTED_FORMATS

    @classmethod
    def inspect(cls, image_id: str, storage_path: str, storage_root: str) -> ImageMetadata:
        """Read image metadata while keeping provider-specific decoding internal."""

        path = cls.resolve_path(storage_path, storage_root)
        if not path.is_file():
            raise FileNotFoundError(f"Image file not found: {path}")
        if path.suffix.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {path.suffix}")

        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for image metadata and pixel analysis") from exc

        with Image.open(path) as image:
            width, height = image.size
            image_format = (image.format or path.suffix.lstrip(".")).lower()

        return ImageMetadata(
            image_id=image_id,
            storage_path=storage_path,
            format=image_format,
            width=width,
            height=height,
            file_size_bytes=path.stat().st_size,
        )

    @classmethod
    def load_grayscale_pixels(cls, storage_path: str, storage_root: str) -> tuple[list[list[float]], int, int]:
        """Load an image as grayscale rows for deterministic local analysis."""

        path = cls.resolve_path(storage_path, storage_root)
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for image pixel analysis") from exc

        with Image.open(path) as image:
            gray = image.convert("L")
            width, height = gray.size
            data_reader = getattr(gray, "get_flattened_data", gray.getdata)
            pixels = list(data_reader())
        rows = [pixels[offset : offset + width] for offset in range(0, len(pixels), width)]
        return rows, width, height

    @classmethod
    def read_image_bytes(cls, storage_path: str, storage_root: str) -> bytes:
        """Read validated image bytes for an optional provider adapter."""

        path = cls.resolve_path(storage_path, storage_root)
        return path.read_bytes()
