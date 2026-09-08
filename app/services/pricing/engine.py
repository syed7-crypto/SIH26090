"""Deterministic, explainable pricing for artisan products.

This module deliberately does not call an AI provider.  Prices are derived
only from the artisan-supplied cost inputs and the supplied market-reference
records, making every number reproducible and suitable for review.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from statistics import median
from typing import Any, Iterable, Mapping

from .market_references import validate_market_reference


MONEY_PLACES = Decimal("0.01")
PRICE_ROUNDING_INCREMENT = Decimal("10")
SUPPORTED_CURRENCY = "INR"

# Client-facing collection guidance only. These values are never used as
# defaults in the deterministic price calculation.
MISSING_INPUT_QUESTIONS = {
    "material": {"question": "How much raw material do you use for one product?", "guidance": "Include the actual material cost for this one item.", "input_type": "currency"},
    "labour_hours": {"question": "How many hours does it take you to make one product?", "guidance": "Include the time you personally spend making this item.", "input_type": "hours"},
    "labour_rate_per_hour": {"question": "What do you usually charge for one hour of your work?", "guidance": "Think about your hourly wage. For skilled craftwork, artisans often charge between ₹80 and ₹200 per hour.", "input_type": "currency_per_hour"},
    "packaging": {"question": "How much do you spend on packaging for this product?", "guidance": "Include boxes, wrapping, labels, or other packaging used for one item. Enter 0 only if it is genuinely zero.", "input_type": "currency"},
    "other": {"question": "Are there any other costs for making one product?", "guidance": "Include genuinely applicable costs not already listed. Enter 0 only if there are none.", "input_type": "currency"},
    "desired_margin_percent": {"question": "What profit margin would you like to keep for business growth?", "guidance": "Profit is separate from your hourly labor wage. A standard margin for handmade products is 15% to 35%.", "input_type": "percentage"},
}


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
    REQUIRED_COST_FIELDS = COST_FIELDS + ("desired_margin_percent",)

    def calculate(
        self,
        product_id: str,
        product: Mapping[str, Any],
        artisan_costs: Mapping[str, Any],
        market_references: Iterable[Mapping[str, Any]],
        currency: str,
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
        if currency != SUPPORTED_CURRENCY:
            raise ValueError(f"currency must be {SUPPORTED_CURRENCY} for the MVP")
        if isinstance(market_references, (str, bytes)):
            raise ValueError("market_references must be an array of objects")
        try:
            iter(market_references)
        except TypeError as error:
            raise ValueError("market_references must be an array of objects") from error

        missing_inputs = [field for field in self.REQUIRED_COST_FIELDS if field not in artisan_costs or artisan_costs[field] is None]
        if missing_inputs:
            return {
                "product_id": product_id,
                "status": "needs_input",
                "missing_inputs": missing_inputs,
                "targeted_questions": self._targeted_questions(missing_inputs),
                "financial_breakdown": None,
            }

        values = {field: self._non_negative(artisan_costs, field) for field in self.COST_FIELDS}
        desired_margin = self._non_negative(artisan_costs, "desired_margin_percent")
        margin_type = artisan_costs.get("margin_type", "gross_margin")
        if margin_type != "gross_margin":
            raise ValueError("artisan_costs.margin_type must be gross_margin")
        if desired_margin >= Decimal("100"):
            raise ValueError("desired_margin_percent must be less than 100")

        labour_cost = values["labour_hours"] * values["labour_rate_per_hour"]
        total_cost = values["material"] + labour_cost + values["packaging"] + values["other"]
        target_price = total_cost / (Decimal("1") - (desired_margin / Decimal("100")))

        comparable_prices, sources, matching_basis = self._comparable_prices(product, market_references)
        market = self._market_summary(comparable_prices, sources)
        suggested_minimum, suggested_maximum = self._suggested_range(target_price, market)
        market_viability = self._market_viability(target_price, market)

        return {
            "product_id": product_id,
            "status": "priced",
            "financial_breakdown": self._financial_breakdown(
                total_cost, labour_cost, values["material"], values["packaging"],
                values["other"], target_price,
            ),
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
                "margin_type": margin_type,
                "currency": currency,
                "market_reference": market,
                "market_matching_basis": matching_basis,
                "market_viability": market_viability,
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

    @staticmethod
    def _targeted_questions(missing_inputs: Iterable[str]) -> list[dict[str, str]]:
        return [{"field": field, **MISSING_INPUT_QUESTIONS[field]} for field in missing_inputs]

    @staticmethod
    def _financial_breakdown(total_cost: Decimal, labour_cost: Decimal, material: Decimal, packaging: Decimal, other: Decimal, target_price: Decimal) -> dict[str, float]:
        profit_margin_amount = target_price - total_cost
        return {
            "break_even_price": _money(PricingEngine._round_customer_price(total_cost)),
            "artisan_take_home": _money(labour_cost + profit_margin_amount),
            "reinvestment_fund": _money(material + packaging + other),
            "profit_margin_amount": _money(profit_margin_amount),
        }

    def _comparable_prices(
        self, product: Mapping[str, Any], records: Iterable[Mapping[str, Any]]
    ) -> tuple[list[Decimal], list[str], str]:
        category = _normalise(product.get("category"))
        material = _normalise(product.get("material"))
        craft_type = _normalise(product.get("craft_type"))
        if not category:
            return [], [], "none (product category is unavailable)"

        compatible: list[Mapping[str, Any]] = []
        for record in records:
            validate_market_reference(record)
            if _normalise(record.get("category")) != category:
                continue
            record_material = _normalise(record.get("material"))
            record_craft = _normalise(record.get("craft_type"))
            if (material and record_material and record_material != material) or (craft_type and record_craft and record_craft != craft_type):
                continue
            compatible.append(record)

        stages: list[tuple[str, tuple[tuple[str, str], ...]]] = []
        if material and craft_type:
            stages.append(("category + material + craft_type", ((material, "material"), (craft_type, "craft_type"))))
        if material:
            stages.append(("category + material", ((material, "material"),)))
        if craft_type:
            stages.append(("category + craft_type", ((craft_type, "craft_type"),)))
        stages.append(("category only", ()))
        for basis, attributes in stages:
            selected = [record for record in compatible if all(_normalise(record.get(field)) == value for value, field in attributes)]
            if selected:
                return self._prices_and_sources(selected, basis)
        return [], [], "none (no attribute-compatible category records)"

    @staticmethod
    def _prices_and_sources(records: Iterable[Mapping[str, Any]], basis: str) -> tuple[list[Decimal], list[str], str]:
        prices: list[Decimal] = []
        sources: list[str] = []
        for record in records:
            try:
                price = Decimal(str(record["price"]))
            except Exception as error:
                raise ValueError("market reference price must be a number") from error
            if not price.is_finite() or price < 0:
                raise ValueError("market reference price must be finite and non-negative")
            prices.append(price)
            source = record["source"].strip()
            if source not in sources:
                sources.append(source)
        return prices, sources, basis

    @staticmethod
    def _market_summary(prices: list[Decimal], sources: list[str]) -> dict[str, Any]:
        if not prices:
            return {"sample_size": 0, "minimum": None, "maximum": None, "median": None, "sources": []}
        return {
            "sample_size": len(prices),
            "minimum": _money(min(prices)),
            "maximum": _money(max(prices)),
            "median": _money(median(prices)),
            "sources": sources,
        }

    @staticmethod
    def _suggested_range(target: Decimal, market: Mapping[str, Any]) -> tuple[Decimal, Decimal]:
        # The lower bound is never below the price needed to achieve the
        # artisan's requested margin.  If comparable prices support a higher
        # position, their median informs the upper end of the range.
        minimum = PricingEngine._round_customer_price(target)
        market_median = market["median"]
        anchor = max(target, Decimal(str(market_median))) if market_median is not None else target
        maximum = PricingEngine._round_customer_price(anchor * Decimal("1.10"))
        return minimum, maximum

    @staticmethod
    def _round_customer_price(value: Decimal) -> Decimal:
        """Round up to a customer-friendly ₹10 price without reducing margin."""

        return (
            (value / PRICE_ROUNDING_INCREMENT).to_integral_value(rounding=ROUND_CEILING)
            * PRICE_ROUNDING_INCREMENT
        )

    @staticmethod
    def _market_viability(target: Decimal, market: Mapping[str, Any]) -> dict[str, str]:
        """State whether the requested-margin floor can fit the market range."""

        if not market["sample_size"]:
            return {
                "status": "no_market_data",
                "message": "No comparable market records are available to assess price viability.",
            }

        market_minimum = Decimal(str(market["minimum"]))
        market_maximum = Decimal(str(market["maximum"]))
        if target > market_maximum:
            return {
                "status": "above_market_range",
                "message": "The requested-margin price floor is above every matched market reference; review costs, margin, or positioning.",
            }
        if target < market_minimum:
            return {
                "status": "below_market_range",
                "message": "The requested-margin price floor is below the matched market range; the product may support a higher market position.",
            }
        return {
            "status": "within_market_range",
            "message": "The requested-margin price floor falls within the matched market range.",
        }

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
        currency=input_data.get("currency"),
    )
