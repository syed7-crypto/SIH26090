# API and AI Provider Usage

The current provider strategy is Google Gemini API. Provider integration is
planned but not implemented in this foundation.

```text
GEMINI_VISION_KEY  → Product Media Intelligence / image understanding
GEMINI_SPEECH_KEY  → Voice & Language Intelligence
GEMINI_CATALOG_KEY → Catalogue generation
```

Pricing Intelligence is deliberately outside this provider boundary. It is a
deterministic calculation service and does not access `GEMINI_PRICING_KEY`, a
model setting, or any external API. Existing pricing-named configuration
placeholders are not used by the Pricing Engine or its HTTP route.

The intended boundary is:

```text
Application Logic
      ↓
Internal AI Service Interface
      ↓
Provider Implementation
      ↓
Gemini
```

This is not a multi-provider framework yet. It is a separation point so a
future provider or model can be introduced without rewriting business logic.
Model names must come from configuration (`GEMINI_*_MODEL`), not be scattered
through source code.

Security and reliability rules:

- Never commit `.env` or hardcode API keys.
- Never expose backend API keys to the frontend.
- Handle provider/API failures explicitly.
- Validate structured model responses against the shared schema and reject or
  report invalid output.
- Separate environment-variable names do not inherently provide separate
  quota. Multiple names or keys must not be presented as automatically
  multiplying Gemini quota.

