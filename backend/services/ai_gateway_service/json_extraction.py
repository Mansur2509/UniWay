from __future__ import annotations

import json
import re

_FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def parse_json_response(raw_text: str) -> dict:
    """Best-effort extraction of a single JSON object from a Gemini text response.

    Even with `responseMimeType: "application/json"` set, a model can still
    wrap its answer in a ```json fence or add stray whitespace/prose. Tries,
    in order: the raw text as-is, the stripped text, a fenced ```json``` (or
    plain ```) block, then the first balanced `{...}` object found in the
    text. Never accepts arbitrary prose as data -- every candidate must parse
    as valid JSON on its own. Raises the last `json.JSONDecodeError`
    encountered if nothing parses.
    """

    candidates = [raw_text]

    stripped = raw_text.strip()
    if stripped != raw_text:
        candidates.append(stripped)

    fence_match = _FENCE_PATTERN.search(raw_text)
    if fence_match:
        candidates.append(fence_match.group(1).strip())

    balanced = _extract_balanced_object(stripped)
    if balanced is not None:
        candidates.append(balanced)

    last_error: json.JSONDecodeError | None = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as error:
            last_error = error
    raise last_error


def _extract_balanced_object(text: str) -> str | None:
    """Return the first balanced `{...}` substring, respecting quoted strings
    so braces inside string values don't unbalance the count. Returns None if
    no complete, balanced object is found.
    """

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None
