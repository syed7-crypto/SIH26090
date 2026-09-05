"""Deterministic image quality metrics for the first Photo Intelligence slice."""

from math import log10

from .schemas import ImageQuality
from .visibility_analyzer import estimate_visibility


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: list[float]) -> float:
    if not values:
        return 0.0
    average = _mean(values)
    return _mean([(value - average) ** 2 for value in values])


def analyze_pixels(pixels: list[list[float]], width: int, height: int) -> ImageQuality:
    """Analyze grayscale pixels without making an object-recognition claim.

    ``blur_score`` is based on the variance of a 3x3 Laplacian response.
    It is a relative sharpness indicator, not a camera-specific probability.
    """

    flat = [value for row in pixels for value in row]
    brightness = _mean(flat)
    brightness_score = _clamp(100.0 - abs(brightness - 128.0) * 100.0 / 128.0)

    laplacian_values: list[float] = []
    for y in range(1, max(1, height - 1)):
        for x in range(1, max(1, width - 1)):
            if y >= len(pixels) or x >= len(pixels[y]):
                continue
            center = pixels[y][x]
            neighbors = (
                pixels[y - 1][x], pixels[y + 1][x],
                pixels[y][x - 1], pixels[y][x + 1],
            )
            laplacian_values.append(4 * center - sum(neighbors))
    blur_raw = _variance(laplacian_values)
    blur_score = _clamp(100.0 * log10(1.0 + blur_raw) / log10(1.0 + 5000.0))

    megapixels = (width * height) / 1_000_000 if width and height else 0.0
    resolution_score = _clamp(megapixels * 100.0 / 2.0)
    aspect_ratio = width / height if height else 0.0
    framing_score = _clamp(100.0 - abs(aspect_ratio - 1.0) * 35.0)
    visibility_score, _, visibility_issues = estimate_visibility(pixels, width, height)

    issues: list[str] = []
    if blur_score < 35:
        issues.append("likely_blurry")
    if brightness_score < 35:
        issues.append("poor_exposure")
    if resolution_score < 50:
        issues.append("low_resolution")
    issues.extend(visibility_issues)

    quality_score = round(
        0.40 * blur_score
        + 0.25 * brightness_score
        + 0.20 * resolution_score
        + 0.15 * framing_score,
        2,
    )
    return ImageQuality(
        quality_score=quality_score,
        blur_score=round(blur_score, 2),
        brightness_score=round(brightness_score, 2),
        resolution_score=round(resolution_score, 2),
        framing_score=round(framing_score, 2),
        visibility_score=visibility_score,
        issues=tuple(issues),
    )
