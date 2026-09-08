"""Adapter from Voice/Product Intelligence data to Pricing Engine input.

This module deliberately maps only product attributes already extracted by
Voice Intelligence. Artisan costs remain a separate structured input because
the current Voice ``ProductInfo`` has no cost fields.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping


VOICE_PRODUCT_FIELDS = ("category", "material", "craft_type")


def map_voice_product_to_pricing_input(
    product_id: str,
    voice_product: Mapping[str, Any] | object,
    artisan_costs: Mapping[str, Any] | None,
    *,
    currency: str = "INR",
    market_references: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build Pricing Engine input from structured Voice ``ProductInfo`` data.

    The mapper supports the Voice ``ProductInfo`` dataclass and its dictionary
    representation from ``VoiceProcessingResult.to_dict()``. Missing product
    attributes and costs are preserved as null/missing; nothing is inferred.
    """
    if is_dataclass(voice_product) and not isinstance(voice_product, type):
        source: Mapping[str, Any] = asdict(voice_product)
    elif isinstance(voice_product, Mapping):
        source = voice_product
    else:
        source = {field: getattr(voice_product, field, None) for field in VOICE_PRODUCT_FIELDS}

    return {
        "product_id": product_id,
        "currency": currency,
        "product": {field: source.get(field) for field in VOICE_PRODUCT_FIELDS},
        "artisan_costs": dict(artisan_costs) if artisan_costs is not None else {},
        "market_references": list(market_references) if market_references is not None else [],
    }


def map_voice_result_to_pricing_input(
    voice_result: Mapping[str, Any] | object,
    artisan_costs: Mapping[str, Any] | None,
    *,
    currency: str = "INR",
    market_references: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build Pricing input from ``VoiceProcessingResult`` or its ``to_dict`` output."""
    if isinstance(voice_result, Mapping):
        return map_voice_product_to_pricing_input(
            voice_result.get("product_id"), voice_result.get("product", {}), artisan_costs,
            currency=currency, market_references=market_references,
        )
    return map_voice_product_to_pricing_input(
        getattr(voice_result, "product_id", None), getattr(voice_result, "product", None), artisan_costs,
        currency=currency, market_references=market_references,
    )
