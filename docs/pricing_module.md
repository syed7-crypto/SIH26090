# Pricing Intelligence

`app.services.pricing.calculate_pricing` is a standalone deterministic service.
It accepts an input object with `product_id`, `product`, `artisan_costs`, and
`market_references`, and returns only the `product_id` and pricing-owned
`pricing` fragment. It neither calls an AI provider nor reads credentials.

Cost input fields are required: `material`, `labour_hours`,
`labour_rate_per_hour`, `packaging`, `other`, and `desired_margin_percent`.
All must be finite non-negative numbers. The desired margin is a **gross
margin**, so the target floor is `total_cost / (1 - margin / 100)` and a margin
of 100 or greater is invalid.

Market records are compared by normalized category. When product material or
craft type is known, records with contradictory known values are excluded;
records that leave either attribute unspecified can still serve as broader
comparables. The module reports sample count, minimum, maximum, and median.

The suggested lower price is the target price needed to preserve the requested
margin. The upper price is 10% above the higher of that target and the matched
market median. With no comparable records, it is 10% above the target. This
makes the trade-off explicit instead of producing an unexplained single price.

Run the module tests with:

```powershell
python -m unittest tests.test_pricing_engine
```
