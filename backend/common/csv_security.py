from __future__ import annotations

CSV_FORMULA_PREFIXES = ("=", "+", "-", "@")


def neutralize_spreadsheet_formula(value) -> str:
    """Return a CSV-safe display value that spreadsheet apps treat as text."""

    text = "" if value is None else str(value)
    candidate = text.lstrip(" \t\r\n")
    if candidate.startswith(CSV_FORMULA_PREFIXES):
        return f"'{text}"
    return text
