**SIH26090 — AI-Driven Market Linkage and Smart Cataloging**

Mobile application and backend for **SIH Problem ID SIH26090**: *“AI-Driven Market Linkage and Smart Cataloging Mobile Application for Marginalized Artisans.”*

The system helps artisans convert product photos, voice descriptions, and cost data into reliable, market-ready product intelligence (catalogue content, pricing guidance, and readiness scores).

---

## Overview

Artisans upload product images, record voice notes (in local languages), and provide cost information. The system processes these inputs through modular AI services and produces structured product intelligence that can be used for cataloguing, pricing, and market readiness.

**Core goal**: Turn raw artisan inputs into trustworthy, schema-compliant product data without hallucinating missing information.

---

## Product Flow

```text
Artisan
  │
  ├── Product Photos
  ├── Voice Description (local language)
  └── Cost Information
          │
          ▼
┌─────────────────────────────────────┐
│     Product Intelligence Layer      │
│  ┌───────────────────────────────┐  │
│  │ Product Media Intelligence    │  │
│  │ (Vision / Image Analysis)     │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Voice & Language Intelligence │  │
│  │ (Speech / Transcription)      │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Catalogue Generation          │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Pricing Intelligence          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
          │
          ▼
Market-ready Product
(Catalogue + Pricing + Readiness)
```

All modules communicate via a shared **Product Intelligence** contract (`backend/app/schemas/product_intelligence.json`) keyed by `product_id`.

---

## Architecture

```text
┌──────────────────┐          ┌──────────────────────────────────────┐
│  Flutter App     │  HTTP    │  FastAPI Backend                     │
│  (frontend/)     │ ───────► │  (backend/)                          │
│                  │          │                                      │
│  • Image/Voice   │          │  /api/.../photos                     │
│    capture       │          │  /api/.../voice                      │
│  • Cost forms    │          │  /api/v1/products/{id}/pricing/...   │
│  • Firebase      │          │                                      │
│    (Firestore)   │          │  Services:                           │
└──────────────────┘          │  • vision/   (media intelligence)    │
                              │  • speech/   (voice & language)      │
                              │  • catalogue/                        │
                              │  • pricing/  (deterministic engine)  │
                              └──────────────────────────────────────┘
                                          │
                                          ▼
                              Shared Schema + Storage Paths
```

- **Backend**: Python 3.10+, FastAPI, Google Gemini (via `google-genai`), Pillow, optional `rembg`.
- **Frontend**: Flutter (cross-platform: Android, iOS, Web, Desktop) with `image_picker`, `record`, `http`, Firebase Core + Cloud Firestore.
- **Data contract**: Strict JSON Schema. Values are real data only — use `null` / `[]` / `0` only when genuinely applicable. Never invent information.

---

## Repository Structure

```text
SIH26090/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── api/                      # FastAPI routers & main app
│   │   │   ├── main.py
│   │   │   ├── pricing.py
│   │   │   └── routes/
│   │   │       ├── photos.py
│   │   │       └── voice.py
│   │   ├── config/                   # Settings / env loading
│   │   ├── core/
│   │   ├── schemas/
│   │   │   └── product_intelligence.json   # Shared contract
│   │   ├── services/
│   │   │   ├── vision/               # Product Media Intelligence
│   │   │   ├── speech/               # Voice & Language
│   │   │   ├── catalogue/
│   │   │   └── pricing/              # Pricing Intelligence
│   │   └── utils/
│   ├── docs/                         # Architecture, ownership, modules
│   ├── tests/
│   ├── data/
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                         # Flutter mobile/web app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   ├── services/
│   │   ├── models/
│   │   ├── state/
│   │   └── widgets/
│   ├── android/ ios/ web/ ...
│   └── pubspec.yaml
├── data/
│   └── sample/                       # Non-sensitive sample data only
├── scripts/                          # Dev / maintenance scripts
├── .env.example
├── .gitignore
└── README.md
```

---

## Key Modules & Ownership

| Area | Responsibility | Location |
|------|----------------|----------|
| **Product Media Intelligence** | Image quality, blur/brightness, duplicates, shot type, primary image, readiness score | `backend/app/services/vision/` |
| **Voice & Language Intelligence** | Transcription, language detection, translation | `backend/app/services/speech/` |
| **Catalogue Generation** | Structured product attributes & presentation | `backend/app/services/catalogue/` |
| **Pricing Intelligence** | Cost → suggested price range (deterministic, INR), market references, explainability | `backend/app/services/pricing/` |
| **Dataset / Evaluation** | Approved sample data & tests | `data/sample/`, `backend/tests/` |
| **Frontend / UI & Integration** | Capture UI, API calls, Firebase, end-to-end flows | `frontend/` |

**Team rule**: Work primarily inside your assigned module. Coordinate before changing another module’s interface or schema.

Detailed ownership notes: `backend/docs/module_ownership.md`.

---

## Shared Schema Highlights

The contract (`backend/app/schemas/product_intelligence.json`) requires:

- `product_id`
- `media` (images with quality scores, types, readiness)
- `product` (name, category, material, craft type, dimensions, etc.)
- `voice` (language, transcript, translation, confidence)
- `pricing` (costs, labour, margin, market reference, suggested range, confidence, explanation)

**Output rule**: Return only reliable values. Never hallucinate.

---

## Setup

### Prerequisites

- Python ≥ 3.10
- Flutter SDK (latest stable) + platform tooling (Android Studio / Xcode as needed)
- Git

### 1. Clone

```bash
git clone https://github.com/syed7-crypto/SIH26090.git
cd SIH26090
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Copy environment template (from repo root):

```bash
cp ../.env.example .env
# Edit .env with your Gemini keys and model names
```

Relevant variables (see `.env.example`):

```text
APP_ENV=development
LOG_LEVEL=INFO
STORAGE_ROOT=data/uploads

GEMINI_VISION_KEY=...
GEMINI_SPEECH_KEY=...
GEMINI_CATALOG_KEY=...
GEMINI_PRICING_KEY=...

GEMINI_VISION_MODEL=...
GEMINI_SPEECH_MODEL=...
GEMINI_CATALOG_MODEL=...
GEMINI_PRICING_MODEL=...
```

**Never commit `.env` or expose keys to the frontend.**

Run foundation / module tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
# or specific modules, e.g.
python -m unittest tests.test_pricing_engine
```

Start the API (from `backend/`):

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI is available at `http://localhost:8000/docs` (when running).

### 3. Frontend

```bash
cd frontend
flutter pub get
flutter run
```

Configure Firebase as needed (`firebase_options.dart`, `firebase.json`). The app uses `image_picker`, `record`, `http`, and Cloud Firestore.

---

## API Surface (Current)

- Photos routes (`app/api/routes/photos.py`)
- Voice routes (`app/api/routes/voice.py`)
- Pricing: `POST /api/v1/products/{product_id}/pricing/analyze`

CORS is enabled for localhost in development.

See `backend/docs/api_usage.md` for provider boundaries and security notes.

---

## Development Principles

- Modules are independently testable.
- Interfaces are explicit and schema-compatible.
- Dependencies are added only when real code needs them.
- Small, understandable commits.
- Provider calls stay behind internal service interfaces (Gemini is the current provider).
- Coordinate before changing shared contracts or another teammate’s module.

Further guidance:

- `backend/docs/architecture.md`
- `backend/docs/development.md`
- `backend/docs/integration.md`
- `backend/docs/pricing_module.md`
- `backend/docs/voice_module.md`

---

## Data Guidelines

- `data/sample/` is for small, non-sensitive, approved sample files only.
- Do **not** commit personal artisan data, production uploads, credentials, or unapproved datasets.
- Local uploads are git-ignored.

---

## Current Status

The repository contains a solid foundation:

- Shared schema and modular service boundaries
- Working vision pipeline components (quality, duplicates, shot classification, etc.)
- Deterministic pricing engine with explainability
- FastAPI endpoints for photos, voice, and pricing
- Flutter client skeleton with media capture and Firebase integration

AI provider wiring and full end-to-end mobile flows continue to evolve. Contributions should respect module ownership and the shared contract.

---

## License / About

Smart India Hackathon (SIH) project repository.  
See individual docs under `backend/docs/` for deeper module design and integration rules.

For questions about ownership or integration, coordinate with the relevant module owner before making cross-cutting changes.
