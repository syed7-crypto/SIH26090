# Pricing Intelligence

`app.services.pricing.calculate_pricing` is a standalone deterministic service.
It accepts an input object with `product_id`, `product`, `artisan_costs`, and
`market_references`, plus a required `currency` of `"INR"`, and returns only the `product_id` and pricing-owned
`pricing` fragment. It neither calls an AI provider nor reads credentials.

## Market-reference dataset

The MVP dataset location is `data/sample/market_references.json`. It is an
intentionally empty JSON array: do not insert invented prices or unapproved
sources. Add only team-approved INR records in this structure:

```json
[
  {
    "category": "handmade bags",
    "material": "cotton",
    "craft_type": "handwoven",
    "price": 950,
    "source": "approved source description"
  }
]
```

The application obtains records at its pricing integration boundary, then
passes them into the engine. This keeps file/data access outside the pricing
calculation:

```python
from app.services.pricing import calculate_pricing, load_market_references

result = calculate_pricing({
    "product_id": "ART-001",
    "product": product_from_voice,
    "artisan_costs": artisan_cost_form,
    "market_references": load_market_references(),
    "currency": "INR",
})
```

To calculate a price, the required cost fields are `material`, `labour_hours`,
`labour_rate_per_hour`, `packaging`, `other`, and `desired_margin_percent`.
When one is missing or null, the engine does not guess: it returns
`{"status": "needs_input", "missing_inputs": [...]}`. Explicit zero is valid.
All supplied values must be finite non-negative numbers. The desired margin is a **gross
margin**, so the target floor is `total_cost / (1 - margin / 100)` and a margin
of 100 or greater is invalid. The result states `margin_type: "gross_margin"`
so that the current business meaning is visible to every integration. Changing
to markup pricing later is a product decision and requires an explicit formula
change rather than silently reinterpreting saved percentages.

Market records are compared by normalized category. When product material or
craft type is known, records with contradictory known values are excluded;
records that leave either attribute unspecified can still serve as broader
comparables. The module reports sample count, minimum, maximum, and median.
It also returns the unique `sources` for the matched records, allowing the
recommendation to be reviewed against its market evidence.
If there are no records, those three statistics are `null`, which the shared
schema explicitly permits because they are genuinely unknown.

The suggested lower price is the target price needed to preserve the requested
margin. The upper price starts at 10% above the higher of that target and the
matched market median. Optional craft positioning can add at most 10% to this
upper-range anchor. A historical rising/falling trend can add or subtract at
most 3% more, calculated as the observed change divided by five and bounded to
±3%. Stable or insufficient trends add 0%. These signals never lower the cost
floor, and trend cannot dominate market evidence. With no comparable records,
the range remains cost-and-margin based. This makes the trade-off explicit
instead of producing an unexplained single price.
For the INR MVP, both suggested endpoints are rounded **up** to the next ₹10;
this preserves the requested margin while producing customer-facing prices.
`pricing.market_viability` makes the result explicit when the desired-margin
floor is above, within, or below the matched market range.

Run the module tests with:

```powershell
python -m unittest tests.test_pricing_engine
```

## Voice and API integration

`map_voice_product_to_pricing_input` maps the fields currently present in the
Voice `ProductInfo`: name, category, subcategory, material, color, craft type,
description, dimensions, weight, usage, pattern, special features, and
production time. It also safely accepts optional pricing-side fields such as
craft complexity, craftsmanship level, and photo evidence when supplied by a
future structured integration. Voice does not currently produce artisan costs,
craft complexity, craftsmanship level, or photo scores, so these stay separate
optional inputs and are never inferred from a transcript.

The backend endpoint is:

```text
POST /api/v1/products/{product_id}/pricing/analyze
```

It accepts structured `currency`, `product`, `artisan_costs`, and optional
`market_references`. Omitted market references load the deliberately empty
approved dataset. A `needs_input` result returns HTTP 200 because it is an
expected follow-up state; invalid supplied data returns HTTP 422.

## Explainability and targeted guidance

Every `priced` result adds a top-level `financial_breakdown` derived from the
same existing Decimal calculation: `break_even_price` (rounded up to ₹10),
`artisan_take_home`, `reinvestment_fund`, and `profit_margin_amount`. These
are analytical outputs only; they do not alter the target price or range.

A `needs_input` result keeps its stable `missing_inputs` field, adds ordered
`targeted_questions` objects (`field`, `question`, `guidance`, `input_type`),
and sets `financial_breakdown` to `null`. Guidance is for collection UX only:
it never supplies a default cost, labour rate, or margin.

## Extended product evidence

The Voice mapper copies available structured fields such as name, category,
subcategory, material, color, craft type, description, dimensions, weight,
usage, pattern, special features, and production time. Optional fields such as
`craft_complexity`, `craftsmanship_level`, and photo evidence are copied only
when present. Missing values stay missing; no costs or attributes are inferred
from free-form text.

`product.craft_complexity` (0-100) and `product.craftsmanship_level` (`low`,
`medium`, or `high`) are optional positioning signals. Their combined,
deterministic adjustment is capped at 10% and affects only the upper suggested
range anchor. It never lowers the sustainable cost/margin floor.

Photo quality is evidence, not a price multiplier. `photo_quality_score`,
`photo_readiness_score`, or `photo_readiness.score` is grouped as weak (0-39),
moderate (40-69), or strong (70-100). It can improve the confidence
explanation, but never increases price or reduces cost recovery.

## Market matching and trends

Reference records may optionally include `subcategory`, `region`, `period` or
`date`, and `demand_trend`. Matching uses the most specific compatible basis:
category + material + craft type, category + material, category + craft type,
category + subcategory, then category only. Known contradictory attributes and
incompatible categories are excluded.

`pricing.market_trend` compares early and late median prices only when at least
four dated records across two periods exist. Movement below 5% is `stable`;
otherwise the result is `rising` or `falling`. Insufficient evidence returns
`insufficient_data`. Date-only, naive datetime, UTC, and mixed ISO values are
normalized deterministically; invalid or missing dates are ignored. This is
historical reference analysis only; the module does not scrape marketplaces or
claim live demand data.

For terminology migration, legacy `financial_breakdown` keys remain unchanged.
The additive `pricing.financial_terms` object provides `cost_recovery`,
`labour_earnings`, `profit_amount`, and `non_labour_costs`. The old
`reinvestment_fund` name is retained only as a legacy response field; it does
not assert that the artisan reinvests that amount. No reinvestment allocation
is inferred without an explicit future input.
