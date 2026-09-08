"""Pricing HTTP endpoint; no AI or provider calls are made here."""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.pricing import calculate_pricing, load_market_references
from app.services.pricing.input_mapper import map_voice_product_to_pricing_input


logger = logging.getLogger(__name__)


class ProductPricingRequest(BaseModel):
    """Structured request accepted from the application or Voice adapter."""

    currency: str
    product: dict[str, Any] = Field(default_factory=dict)
    artisan_costs: dict[str, Any] = Field(default_factory=dict)
    market_references: list[dict[str, Any]] | None = None


class ConfidenceResponse(BaseModel):
    level: Literal["low", "medium", "high"]
    reason: str


class FinancialBreakdownResponse(BaseModel):
    break_even_price: float
    artisan_take_home: float
    reinvestment_fund: float
    profit_margin_amount: float


class FinancialTermsResponse(BaseModel):
    cost_recovery: float
    labour_earnings: float
    profit_amount: float
    non_labour_costs: float


class MarketReferenceResponse(BaseModel):
    sample_size: int
    minimum: float | None
    maximum: float | None
    median: float | None
    sources: list[str]


class MarketViabilityResponse(BaseModel):
    status: Literal["no_market_data", "above_market_range", "below_market_range", "within_market_range"]
    message: str


class MarketTrendResponse(BaseModel):
    direction: Literal["rising", "falling", "stable", "insufficient_data"]
    change_percent: float | None
    sample_size: int
    pricing_adjustment_percent: float
    message: str


class ProductPositioningResponse(BaseModel):
    available: bool
    adjustment_percent: float
    reason: str


class PhotoEvidenceResponse(BaseModel):
    available: bool
    score: float | None
    band: Literal["weak", "moderate", "strong"] | None = None
    message: str


class SuggestedPriceResponse(BaseModel):
    minimum: float
    maximum: float


class PricedDetailsResponse(BaseModel):
    """Explicit pricing-owned response fields for direct API consumers."""

    costs: dict[str, float]
    labour: dict[str, float]
    desired_margin_percent: float
    margin_type: Literal["gross_margin"]
    currency: Literal["INR"]
    market_reference: MarketReferenceResponse
    market_matching_basis: str
    market_viability: MarketViabilityResponse
    market_trend: MarketTrendResponse
    product_positioning: ProductPositioningResponse
    photo_evidence: PhotoEvidenceResponse
    financial_terms: FinancialTermsResponse
    suggested_price: SuggestedPriceResponse
    confidence: ConfidenceResponse
    explanation: list[str]


class PricedPricingResponse(BaseModel):
    product_id: str
    status: Literal["priced"]
    financial_breakdown: FinancialBreakdownResponse
    pricing: PricedDetailsResponse


class TargetedQuestionResponse(BaseModel):
    field: str
    question: str
    guidance: str
    input_type: str


class NeedsInputPricingResponse(BaseModel):
    product_id: str
    status: Literal["needs_input"]
    missing_inputs: list[str]
    targeted_questions: list[TargetedQuestionResponse]
    financial_breakdown: None


# This is intentionally separate from product_intelligence.json, which is the
# aggregate media/voice/product document rather than this endpoint's payload.
PricingResponseSchema = Annotated[
    PricedPricingResponse | NeedsInputPricingResponse,
    Field(discriminator="status"),
]


router = APIRouter(prefix="/api/v1/products", tags=["pricing"])


@router.post("/{product_id}/pricing/analyze", response_model=PricingResponseSchema)
def analyze_pricing(product_id: str, request: ProductPricingRequest) -> dict[str, Any]:
    """Return a deterministic recommendation or a targeted input request.

    Omitted market references use the deliberately empty, team-approved
    dataset. An explicitly supplied empty list is also retained as no data.
    """
    market_references = request.market_references
    if market_references is None:
        try:
            market_references = load_market_references()
        except ValueError as error:
            logger.warning("Market-reference dataset could not be loaded; using no market data: %s", error)
            market_references = []
    pricing_input = map_voice_product_to_pricing_input(
        product_id, request.product, request.artisan_costs,
        currency=request.currency, market_references=market_references,
    )
    try:
        return calculate_pricing(pricing_input)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
