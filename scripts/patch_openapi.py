#!/usr/bin/env python3
"""
Patches known schema violations in the comdirect Swagger specification.

comdirect defines several primitive wrapper types (e.g. CurrencyString,
DateString) as objects, but the API returns plain strings.

This script normalizes those schemas so code generation works reliably.
"""

import json
from pathlib import Path

SPEC_PATH = Path("tmp/comdirect_openapi.json")

if not SPEC_PATH.exists():
    raise RuntimeError(f"Spec file not found: {SPEC_PATH}")

data = json.loads(SPEC_PATH.read_text())

definitions = data.get("definitions")
if not definitions:
    raise RuntimeError("No 'definitions' section found in swagger")


def patch_string(name, description, *, example=None, pattern=None):
    schema = {
        "type": "string",
        "description": description,
    }
    if example is not None:
        schema["example"] = example
    if pattern is not None:
        schema["pattern"] = pattern
    definitions[name] = schema


# ------------------------------------------------------------------
# Primitive wrapper fixes (API returns plain strings)
# ------------------------------------------------------------------

patch_string(
    "CurrencyString",
    "ISO-4217 currency code",
    example="EUR",
)

patch_string(
    "DateString",
    "ISO-8601 date (YYYY-MM-DD)",
    example="2024-09-30",
    pattern=r"^\d{4}-\d{2}-\d{2}$",
)

patch_string(
    "TimestampString",
    "ISO-8601 timestamp",
    example="2024-09-30T12:34:56Z",
)

patch_string(
    "PercentageString",
    "Percentage encoded as string",
    example="12.34",
)
# DateTimeString
patch_string(
    "DateTimeString",
    "ISO-8601 date-time (YYYY-MM-DDThh:mm:ssZ)",
    example="2024-09-30T12:34:56Z",
)

SPEC_PATH.write_text(json.dumps(data, indent=2))
print("✔ OpenAPI spec patched successfully")
