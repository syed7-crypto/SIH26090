# Development

This is a Python project. Keep the foundation small while the six-person team
implements modules independently.

## Rules

- Use a virtual environment and install dependencies from `requirements.txt`.
- Keep secrets in local environment variables or `.env`; never commit `.env`.
- Write tests for module logic and keep modules independently testable.
- Keep modules separated and avoid unnecessary dependencies.
- Preserve the shared schema and its `storage_path` field.
- Do not silently modify another person's module; coordinate integration changes.
- Use small, understandable commits.
- Document important architectural decisions.

## Local workflow

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m unittest discover -s tests -p "test_*.py"
```

Only add a dependency when implemented code genuinely needs it. Do not add AI
SDKs or frontend dependencies in anticipation of future work.

