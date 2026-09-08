# Architecture

The intended system is a modular pipeline. It is documented here before the
individual AI services are implemented.

```text
Inputs
  ├── Product Images
  ├── Artisan Voice
  └── Cost Information
          ↓
Product Intelligence Layer
          ↓
  ├── Product Media Intelligence
  ├── Voice & Language Intelligence
  ├── Catalogue Generation
  └── Pricing Intelligence
          ↓
Market-ready Product
```

Modules communicate through structured data and the shared contract at
`app/schemas/product_intelligence.json`. `product_id` is the common identity
used when combining outputs. Each future service should have explicit inputs,
outputs, validation, error behavior, and tests.

The service directories are boundaries, not implementations. Provider-specific
AI calls belong behind internal service interfaces so business logic does not
depend directly on a particular model or SDK.

