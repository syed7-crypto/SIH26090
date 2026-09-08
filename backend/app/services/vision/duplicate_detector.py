"""Exact and perceptual duplicate detection for stored product images."""

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .image_processor import ImageProcessor


@dataclass(frozen=True)
class DuplicateResult:
    """Duplicate status for one image relative to an ordered image set."""

    storage_path: str
    is_duplicate: bool
    duplicate_of: str | None = None
    exact_match: bool = False
    hamming_distance: int | None = None


class DuplicateDetector:
    """Find exact and visually near-identical images without an AI provider."""

    @staticmethod
    def file_hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as image_file:
            for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @classmethod
    def perceptual_hash(cls, storage_path: str, storage_root: str, size: int = 8) -> int:
        """Return an average hash represented as bits for Hamming comparisons."""

        path = ImageProcessor.resolve_path(storage_path, storage_root)
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for perceptual duplicate detection") from exc

        with Image.open(path) as image:
            resized = image.convert("L").resize((size, size))
            data_reader = getattr(resized, "get_flattened_data", resized.getdata)
            pixels = list(data_reader())
        average = sum(pixels) / len(pixels)
        result = 0
        for pixel in pixels:
            result = (result << 1) | int(pixel >= average)
        return result

    @staticmethod
    def _hamming_distance(first: int, second: int) -> int:
        return (first ^ second).bit_count()

    @classmethod
    def find_duplicates(
        cls,
        storage_paths: list[str],
        storage_root: str,
        hamming_threshold: int = 4,
    ) -> list[DuplicateResult]:
        """Analyze paths in order; the first occurrence remains canonical."""

        known_files: dict[str, str] = {}
        known_hashes: list[tuple[str, int]] = []
        results: list[DuplicateResult] = []

        for storage_path in storage_paths:
            path = ImageProcessor.resolve_path(storage_path, storage_root)
            exact = cls.file_hash(path)
            if exact in known_files:
                results.append(DuplicateResult(storage_path, True, known_files[exact], True, 0))
                continue

            image_hash = cls.perceptual_hash(storage_path, storage_root)
            match = next(
                ((canonical, cls._hamming_distance(image_hash, prior_hash)) for canonical, prior_hash in known_hashes
                 if cls._hamming_distance(image_hash, prior_hash) <= hamming_threshold),
                None,
            )
            if match is None:
                known_files[exact] = storage_path
                known_hashes.append((storage_path, image_hash))
                results.append(DuplicateResult(storage_path, False))
            else:
                canonical, distance = match
                results.append(DuplicateResult(storage_path, True, canonical, False, distance))

        return results
