# SIH26090 — AI-Driven Market Linkage and Smart Cataloging

This repository is the Python foundation for SIH Problem ID **SIH26090**:
“AI-Driven Market Linkage and Smart Cataloging Mobile Application for
Marginalized Artisans.” The objective is to help artisans turn product photos,
voice information, and cost information into reliable, market-ready product
intelligence. This repository currently contains setup and shared contracts;
the AI modules and mobile application are not implemented yet.

## Product flow

```text
Artisan
  ↓
Photos + Voice + Cost Information
  ↓
AI Processing
  ↓
Product Intelligence
  ↓
Catalogue + Pricing + Market Readiness
  ↓
Market-ready Product
```

The planned module areas are Product Media Intelligence, Voice & Language
Intelligence, Catalogue Generation, Pricing Intelligence, Dataset/Evaluation,
and Frontend/UI & Integration Testing. Six team members own these areas
separately; ownership and coordination rules are documented in
[`docs/module_ownership.md`](docs/module_ownership.md).

## Repository structure

- `app/config/` — environment-backed settings.
- `app/schemas/` — the shared product intelligence data contract.
- `app/services/` — empty service boundaries for future implementations.
- `app/core/` and `app/utils/` — reserved shared foundations.
- `tests/` — foundation and future module tests.
- `docs/` — architecture, development, provider, ownership, and integration guidance.
- `data/sample/` — reserved for approved, non-sensitive sample data.

## Setup

Use Python 3.10 or newer and create a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set values locally as needed. The current
settings loader reads process environment variables; use your shell, IDE, or
deployment environment to load `.env`. Never commit `.env` or expose backend
API keys to a frontend.

Run the foundation test with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Shared schema

The shared contract is [`app/schemas/product_intelligence.json`](app/schemas/product_intelligence.json).
All modules must produce schema-compatible structured data and preserve
`storage_path` for stored image/audio references. Schema values are structural
placeholders, not default outputs: return reliable actual values, use `null`
only when information is genuinely unavailable, `[]` only when there are no
items, and `0` only when the actual value is zero. Never hallucinate missing
information. Do not redesign or silently modify this contract.

## Development principles

Keep modules independently testable, interfaces predictable, dependencies
minimal, and changes small and understandable. Each teammate should work
primarily in their assigned code section and coordinate before changing another
module. See [`docs/development.md`](docs/development.md) and
[`docs/integration.md`](docs/integration.md).

