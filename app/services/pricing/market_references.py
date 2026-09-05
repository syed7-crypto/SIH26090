"""Loading and validation for the MVP's maintained market-reference data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


DEFAULT_MARKET_REFERENCE_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "sample" / "market_references.json"
)


def load_market_references(path: str | Path = DEFAULT_MARKET_REFERENCE_PATH) -> list[dict[str, Any]]:
    """Load team-approved reference records from a JSON array.

    The bundled file is deliberately empty: market prices must be entered only
    after the team has approved their source.  A production application can
    pass its configured dataset path instead of relying on this development
    default.
    """

    dataset_path = Path(path)
    try:
        with dataset_path.open("r", encoding="utf-8") as dataset_file:
            records = json.load(dataset_file)
    except OSError as error:
        raise ValueError(f"market reference dataset could not be read: {dataset_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"market reference dataset is not valid JSON: {dataset_path}") from error

    if not isinstance(records, list):
        raise ValueError("market reference dataset must be a JSON array")
    for record in records:
        validate_market_reference(record)
    return records


def validate_market_reference(record: Mapping[str, Any]) -> None:
    """Validate the required market-reference fields without inventing data."""

    if not isinstance(record, Mapping):
        raise ValueError("each market reference must be an object")
    for field in ("category", "source"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"market reference {field} must be a non-empty string")
    for field in ("material", "craft_type"):
        if record.get(field) is not None and (
            not isinstance(record[field], str) or not record[field].strip()
        ):
            raise ValueError(f"market reference {field} must be a non-empty string or null")
    if "price" not in record:
        raise ValueError("each market reference requires price")
