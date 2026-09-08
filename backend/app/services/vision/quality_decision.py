"""Deterministic decisions for turning raw photos into a usable photo set."""

from dataclasses import dataclass

from .schemas import ImageQuality


@dataclass(frozen=True)
class PhotoDecision:
    status: str
    reason: str
    actions: tuple[str, ...] = ()


def decide_photo(quality: ImageQuality, *, is_duplicate: bool, contrast_score: float) -> PhotoDecision:
    """Choose a conservative action using only explainable local signals."""

    if is_duplicate:
        return PhotoDecision("removed", "Duplicate of another photo")
    if quality.blur_score < 35:
        return PhotoDecision("removed", "Too blurry to recover")
    # ``resolution_score`` is a useful quality contribution, but a moderate
    # low-resolution warning is not by itself a retake decision. Use the
    # actual dimensions when available and reserve retakes for genuinely tiny
    # images that cannot provide useful product detail.
    if quality.width is not None and quality.height is not None:
        extremely_tiny = min(quality.width, quality.height) < 160 or (
            quality.megapixels is not None and quality.megapixels < 0.1
        )
    else:
        extremely_tiny = quality.resolution_score < 20
    if extremely_tiny:
        return PhotoDecision("needs_retake", "Image resolution is too low")
    if quality.visibility_score is not None and quality.visibility_score < 35:
        return PhotoDecision("needs_retake", "Product is not clearly visible")
    if "subject_may_be_cropped" in quality.issues:
        return PhotoDecision("needs_retake", "Product is severely cropped")

    actions: list[str] = []
    if quality.brightness_score < 75:
        actions.append("brightness_corrected")
    if contrast_score < 65:
        actions.append("contrast_improved")
    if 35 <= quality.blur_score < 70:
        actions.append("sharpened")
    if actions:
        return PhotoDecision("enhance", "Photo can be improved safely", tuple(actions))
    return PhotoDecision("kept", "Photo already meets the quality checks")
