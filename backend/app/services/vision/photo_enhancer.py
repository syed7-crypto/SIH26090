"""Conservative, non-generative image enhancement."""

from pathlib import Path

from PIL import Image, ImageEnhance, ImageStat

from .image_processor import ImageProcessor


def contrast_score(image: Image.Image) -> float:
    """Return a bounded local contrast estimate for decision-making."""

    grayscale = image.convert("L")
    deviation = ImageStat.Stat(grayscale).stddev[0]
    return max(0.0, min(100.0, deviation * 100.0 / 64.0))


class PhotoEnhancer:
    """Apply mild Pillow corrections without overwriting the source."""

    def __init__(self, storage_root: str = "data/uploads") -> None:
        self.storage_root = storage_root

    def enhance(
        self,
        storage_path: str,
        output_path: str,
        *,
        brightness_score: float,
        contrast: float,
        blur_score: float,
    ) -> str:
        source = ImageProcessor.resolve_path(storage_path, self.storage_root)
        destination = ImageProcessor.resolve_path(output_path, self.storage_root)
        if source == destination:
            raise ValueError("enhancement output must not overwrite the original image")

        with Image.open(source) as source_image:
            image = source_image.convert("RGB")
            if brightness_score < 75:
                factor = 1.0 + min(0.45, (75.0 - brightness_score) / 100.0)
                image = ImageEnhance.Brightness(image).enhance(factor)
            if contrast < 65:
                factor = 1.0 + min(0.25, (65.0 - contrast) / 100.0)
                image = ImageEnhance.Contrast(image).enhance(factor)
            if 35 <= blur_score < 70:
                image = ImageEnhance.Sharpness(image).enhance(1.15)

            destination.parent.mkdir(parents=True, exist_ok=True)
            image.save(destination, format="PNG" if destination.suffix.lower() == ".png" else "JPEG", quality=92)

        return output_path.replace("\\", "/")
