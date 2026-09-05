"""Deterministic, explainable pricing for artisan products.

This module deliberately does not call an AI provider.  Prices are derived
only from the artisan-supplied cost inputs and the supplied market-reference
records, making every number reproducible and suitable for review.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from statistics import median
from typing import Any, Iterable, Mapping


MONEY_PLACES = Decimal("0.01")


def _money(value: Decimal | int | float | str) -> float:
    """Return a currency amount rounded predictably to two decimal places."""

    return float(Decimal(str(value)).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP))


def _normalise(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    result = " ".join(value.casefold().split())
    return result or None


class PricingEngine:
    """Calculate a pricing result from product, cost, and market inputs."""

    COST_FIELDS = ("material", "labour_hours", "labour_rate_per_hour", "packaging", "other")

    def calculate(
        self,
        product_id: str,
        product: Mapping[str, Any],
        artisan_costs: Mapping[str, Any],
        market_references: Iterable[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Return the pricing-owned JSON fragment for one product.

        ``desired_margin_percent`` is treated as a gross margin: a 25% margin
        means profit is 25% of the final selling price.  It must therefore be
        below 100.  All cost fields are required because the module must not
        invent an artisan's costs.
        """

        if not isinstance(product_id, str) or not product_id.strip():
            raise ValueError("product_id must be a non-empty string")
        if not isinstance(product, Mapping):
            raise ValueError("product must be an object")
        if not isinstance(artisan_costs, Mapping):
            raise ValueError("artisan_costs must be an object")
        if isinstance(market_references, (str, bytes)):
            raise ValueError("market_references must be an array of objects")
        try:
            iter(market_references)
        except TypeError as error:
            raise ValueError("market_references must be an array of objects") from error

        values = {field: self._non_negative(artisan_costs, field) for field in self.COST_FIELDS}
        desired_margin = self._non_negative(artisan_costs, "desired_margin_percent")
        if desired_margin >= Decimal("100"):
            raise ValueError("desired_margin_percent must be less than 100")

        labour_cost = values["labour_hours"] * values["labour_rate_per_hour"]
        total_cost = values["material"] + labour_cost + values["packaging"] + values["other"]
        target_price = total_cost / (Decimal("1") - (desired_margin / Decimal("100")))

        comparable_prices, matching_basis = self._comparable_prices(product, market_references)
        market = self._market_summary(comparable_prices)
        suggested_minimum, suggested_maximum = self._suggested_range(target_price, market)

        return {
            "product_id": product_id,
            "pricing": {
                "costs": {
                    "material": _money(values["material"]),
                    "labour": _money(labour_cost),
                    "packaging": _money(values["packaging"]),
                    "other": _money(values["other"]),
                    "total": _money(total_cost),
                },
                "labour": {
                    "hours": _money(values["labour_hours"]),
                    "rate_per_hour": _money(values["labour_rate_per_hour"]),
                },
                "desired_margin_percent": _money(desired_margin),
                "market_reference": market,
                "suggested_price": {
                    "minimum": _money(suggested_minimum),
                    "maximum": _money(suggested_maximum),
                },
                "confidence": self._confidence(len(comparable_prices), matching_basis),
                "explanation": self._explanation(
                    total_cost, labour_cost, desired_margin, target_price, market, matching_basis,
                    suggested_minimum, suggested_maximum,
                ),
            },
        }

    @staticmethod
    def _non_negative(values: Mapping[str, Any], field: str) -> Decimal:
        if field not in values:
            raise ValueError(f"artisan_costs.{field} is required")
        try:
            number = Decimal(str(values[field]))
        except Exception as error:  # Decimal has several implementation-specific errors.
            raise ValueError(f"artisan_costs.{field} must be a number") from error
        if not number.is_finite() or number < 0:
            raise ValueError(f"artisan_costs.{field} must be a finite non-negative number")
        return number

    def _comparable_prices(
        self, product: Mapping[str, Any], records: Iterable[Mapping[str, Any]]
    ) -> tuple[list[Decimal], str]:
        category = _normalise(product.get("category"))
        material = _normalise(product.get("material"))
        craft_type = _normalise(product.get("craft_type"))
        if not category:
            return [], "none (product category is unavailable)"

        category_records: list[Mapping[str, Any]] = []
        for record in records:
            if not isinstance(record, Mapping):
                raise ValueError("each market reference must be an object")
            if _normalise(record.get("category")) != category:
                continue
            category_records.append(record)

        # Prefer records that do not contradict known product attributes.  A
        # reference with an unknown material/craft remains usable as a broader
        # category comparison.
        filtered = [
            record for record in category_records
            if (not material or not _normalise(record.get("material")) or _normalise(record.get("material")) == material)
            and (not craft_type or not _normalise(record.get("craft_type")) or _normalise(record.get("craft_type")) == craft_type)
        ]
        selected = filtered or category_records
        basis = "category"
        if selected and filtered and (material or craft_type):
            details = [name for name, value in (("material", material), ("craft type", craft_type)) if value]
            basis = "category and " + " / ".join(details)

        prices: list[Decimal] = []
        for record in selected:
            if "price" not in record:
                raise ValueError("each selected market reference requires price")
            try:
                price = Decimal(str(record["price"]))
            except Exception as error:
                raise ValueError("market reference price must be a number") from error
            if not price.is_finite() or price < 0:
                raise ValueError("market reference price must be finite and non-negative")
            prices.append(price)
        return prices, basis if prices else "none (no matching category records)"

    @staticmethod
    def _market_summary(prices: list[Decimal]) -> dict[str, Any]:
        if not prices:
            return {"sample_size": 0, "minimum": None, "maximum": None, "median": None}
        return {
            "sample_size": len(prices),
            "minimum": _money(min(prices)),
            "maximum": _money(max(prices)),
            "median": _money(median(prices)),
        }

    @staticmethod
    def _suggested_range(target: Decimal, market: Mapping[str, Any]) -> tuple[Decimal, Decimal]:
        # The lower bound is never below the price needed to achieve the
        # artisan's requested margin.  If comparable prices support a higher
        # position, their median informs the upper end of the range.
        minimum = target
        market_median = market["median"]
        anchor = max(target, Decimal(str(market_median))) if market_median is not None else target
        maximum = anchor * Decimal("1.10")
        return minimum, maximum

    @staticmethod
    def _confidence(sample_size: int, matching_basis: str) -> float:
        if sample_size == 0:
            return 0.35
        if sample_size == 1:
            return 0.55
        if sample_size < 5:
            return 0.7
        return 0.85 if matching_basis != "category" else 0.75

    @staticmethod
    def _explanation(
        total: Decimal, labour: Decimal, margin: Decimal, target: Decimal,
        market: Mapping[str, Any], basis: str, low: Decimal, high: Decimal,
    ) -> list[str]:
        messages = [
            f"Production cost is ₹{_money(total):.2f}, including ₹{_money(labour):.2f} for labour.",
            f"A {_money(margin):.2f}% desired gross margin requires at least ₹{_money(target):.2f}.",
        ]
        if market["sample_size"]:
            messages.append(
                f"{market['sample_size']} comparable record(s) matched by {basis}; "
                f"their prices range from ₹{market['minimum']:.2f} to ₹{market['maximum']:.2f}, "
                f"with a median of ₹{market['median']:.2f}."
            )
        else:
            messages.append("No comparable market records were available, so the range is cost-and-margin based only.")
        messages.append(f"Suggested selling range: ₹{_money(low):.2f}–₹{_money(high):.2f}.")
        return messages


def calculate_pricing(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Convenience entry point for the module's standard input object."""

    if not isinstance(input_data, Mapping):
        raise ValueError("pricing input must be an object")
    return PricingEngine().calculate(
        product_id=input_data.get("product_id"),
        product=input_data.get("product"),
        artisan_costs=input_data.get("artisan_costs"),
        market_references=input_data.get("market_references", []),
    )
