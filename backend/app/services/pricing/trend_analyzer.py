"""Deterministic trend analysis for dated market-reference records."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from statistics import median
from typing import Any, Iterable, Mapping


MIN_TREND_SAMPLES = 4
MIN_TREND_CHANGE_PERCENT = Decimal("5")
MAX_TREND_PRICING_ADJUSTMENT_PERCENT = Decimal("3")


def _normalise_period(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _period(record: Mapping[str, Any]) -> datetime | None:
    period = _normalise_period(record.get("period"))
    return period if period is not None else _normalise_period(record.get("date"))


def _pricing_adjustment(change: Decimal | None, direction: str) -> float:
    if change is None or direction not in {"rising", "falling"}:
        return 0.0
    bounded = min(
        MAX_TREND_PRICING_ADJUSTMENT_PERCENT,
        max(-MAX_TREND_PRICING_ADJUSTMENT_PERCENT, change / Decimal("5")),
    )
    return float(bounded)


def analyze_market_trend(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Compare early and late medians when dated evidence is sufficient."""

    dated = [(period, Decimal(str(record["price"]))) for record in records if (period := _period(record)) is not None]
    if len(dated) < MIN_TREND_SAMPLES or len({period for period, _ in dated}) < 2:
        return {
            "direction": "insufficient_data",
            "change_percent": None,
            "sample_size": len(dated),
            "pricing_adjustment_percent": 0.0,
            "message": "Not enough dated comparable records are available to identify a market trend.",
        }

    dated.sort(key=lambda item: item[0])
    midpoint = len(dated) // 2
    earlier = median([price for _, price in dated[:midpoint]])
    later = median([price for _, price in dated[midpoint:]])
    if earlier == 0:
        return {
            "direction": "insufficient_data",
            "change_percent": None,
            "sample_size": len(dated),
            "pricing_adjustment_percent": 0.0,
            "message": "The earlier comparable median is zero, so a reliable trend cannot be calculated.",
        }
    change = (later - earlier) * Decimal("100") / earlier
    if abs(change) < MIN_TREND_CHANGE_PERCENT:
        direction = "stable"
    else:
        direction = "rising" if change > 0 else "falling"
    messages = {
        "rising": "Comparable prices increased over the available reference periods.",
        "falling": "Comparable prices decreased over the available reference periods.",
        "stable": "Comparable prices were broadly stable over the available reference periods.",
    }
    return {
        "direction": direction,
        "change_percent": round(float(change), 2),
        "sample_size": len(dated),
        "pricing_adjustment_percent": _pricing_adjustment(change, direction),
        "message": messages[direction],
    }
