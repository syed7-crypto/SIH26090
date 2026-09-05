"""Conservative pixel heuristics for estimated subject visibility."""

from .schemas import ImageQuality


def estimate_visibility(pixels: list[list[float]], width: int, height: int) -> tuple[float, float, tuple[str, ...]]:
    """Estimate foreground visibility and framing from border contrast.

    This is not object detection. It is useful for flagging images whose
    subject is likely lost in a flat background or fills almost the whole frame.
    """

    if not pixels or not width or not height:
        return 0.0, 0.0, ("no_pixels",)

    border = []
    for y, row in enumerate(pixels):
        for x, value in enumerate(row):
            if y in (0, height - 1) or x in (0, width - 1):
                border.append(value)
    background = sum(border) / len(border) if border else 0.0
    threshold = 20.0
    foreground = [value for row in pixels for value in row if abs(value - background) >= threshold]
    occupancy = len(foreground) / (width * height)
    contrast = (sum(abs(value - background) for value in foreground) / len(foreground)) if foreground else 0.0
    contrast_score = min(100.0, contrast * 100.0 / 64.0)
    occupancy_score = max(0.0, 100.0 - abs(occupancy - 0.45) * 180.0)
    visibility_score = round(0.65 * contrast_score + 0.35 * occupancy_score, 2)

    issues = []
    if not foreground:
        issues.append("subject_not_separated")
    elif occupancy < 0.05:
        issues.append("subject_too_small")
    elif occupancy > 0.95:
        issues.append("subject_may_be_cropped")
    if visibility_score < 35:
        issues.append("low_visibility")
    return visibility_score, occupancy, tuple(issues)

