"""Bounded, explainable craft-positioning signals."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping


def craft_positioning(product: Mapping[str, Any]) -> dict[str, Any]:
    """Return an optional bounded premium signal from structured inputs only.

    ``craft_complexity`` is 0-100 and ``craftsmanship_level`` may be low,
    medium, or high. The combined adjustment is capped at 10 percent and is
    applied only to the suggested range anchor, never to the cost floor.
    """

    complexity = product.get("craft_complexity")
    level = product.get("craftsmanship_level")
    if complexity is None and level is None:
        return {"available": False, "adjustment_percent": 0.0, "reason": "No structured craft-positioning signal was provided."}
    if complexity is not None:
        try:
            complexity_value = Decimal(str(complexity))
        except Exception as error:
            raise ValueError("product.craft_complexity must be a number") from error
        if not complexity_value.is_finite() or not 0 <= complexity_value <= 100:
            raise ValueError("product.craft_complexity must be between 0 and 100")
    else:
        complexity_value = Decimal("0")
    level_value = str(level).casefold() if level is not None else None
    level_adjustment = {"low": Decimal("0"), "medium": Decimal("3"), "high": Decimal("5")}
    if level_value not in level_adjustment and level_value is not None:
        raise ValueError("product.craftsmanship_level must be low, medium, or high")
    adjustment = min(Decimal("10"), (complexity_value / Decimal("20")) + level_adjustment.get(level_value, Decimal("0")))
    return {
        "available": True,
        "adjustment_percent": float(adjustment),
        "reason": "Structured craft complexity and craftsmanship signals support a bounded positioning adjustment; they do not change cost recovery.",
    }
