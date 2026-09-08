"""Pricing HTTP endpoint; no AI or provider calls are made here."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.pricing import calculate_pricing, load_market_references
from app.services.pricing.input_mapper import map_voice_product_to_pricing_input


class ProductPricingRequest(BaseModel):
    """Structured request accepted from the application or Voice adapter."""

    currency: str
    product: dict[str, Any] = Field(default_factory=dict)
    artisan_costs: dict[str, Any] = Field(default_factory=dict)
    market_references: list[dict[str, Any]] | None = None


router = APIRouter(prefix="/api/v1/products", tags=["pricing"])


@router.post("/{product_id}/pricing/analyze")
def analyze_pricing(product_id: str, request: ProductPricingRequest) -> dict[str, Any]:
    """Return a deterministic recommendation or a targeted input request.

    Omitted market references use the deliberately empty, team-approved
    dataset. An explicitly supplied empty list is also retained as no data.
    """
    market_references = request.market_references
    if market_references is None:
        market_references = load_market_references()
    pricing_input = map_voice_product_to_pricing_input(
        product_id, request.product, request.artisan_costs,
        currency=request.currency, market_references=market_references,
    )
    try:
        return calculate_pricing(pricing_input)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
