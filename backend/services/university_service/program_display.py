from __future__ import annotations

import re
from collections.abc import Iterable

TRACK_SEPARATOR = " — "


def _clean_fragment(value: str) -> str:
    value = value.strip()
    value = value.strip("-•* ")
    value = value.replace("(", "").replace(")", "")
    return re.sub(r"\s+", " ", value).strip(" ,;")


def _split_tracks(value: str) -> list[str]:
    return [_clean_fragment(part) for part in re.split(r"[,;]", value) if _clean_fragment(part)]


def _expand_track(parent: str, track: str) -> str:
    parent_key = parent.lower()
    track_key = track.strip().replace(".", "").lower()
    if "engineering" in parent_key and track_key == "ee":
        return "Electrical Engineering"
    if ("computer" in parent_key or "computing" in parent_key) and track_key == "cs":
        return "Computer Science"
    if ("econom" in parent_key or "business" in parent_key) and track_key == "econ":
        return "Economics"
    return track


def _track_label(parent: str, track: str) -> str:
    clean_parent = _clean_fragment(parent)
    clean_track = _expand_track(clean_parent, _clean_fragment(track))
    if not clean_parent:
        return clean_track
    if not clean_track:
        return clean_parent
    return f"{clean_parent}{TRACK_SEPARATOR}{clean_track}"


def format_program_display_names(raw_names: Iterable[str]) -> list[str]:
    """Return display-safe program labels without mutating stored raw names.

    The importer may preserve a single parenthetical value or comma-split fragments
    such as "Engineering (Civil", "Mechanical", "EE)". This helper only carries a
    parent context forward after an explicit unmatched "(" in the source sequence.
    """

    labels: list[str] = []
    open_parent: str | None = None

    for raw_name in raw_names:
        value = str(raw_name or "").strip()
        if not value:
            continue

        complete_match = re.match(r"^(.+?)\s*\((.+)\)\s*$", value)
        if complete_match:
            parent, tracks = complete_match.groups()
            labels.extend(_track_label(parent, track) for track in _split_tracks(tracks))
            open_parent = None
            continue

        broken_start = re.match(r"^(.+?)\s*\((.+)$", value)
        if broken_start:
            parent, first_track = broken_start.groups()
            open_parent = _clean_fragment(parent)
            labels.extend(_track_label(open_parent, track) for track in _split_tracks(first_track))
            if ")" in value:
                open_parent = None
            continue

        if open_parent:
            labels.extend(_track_label(open_parent, track) for track in _split_tracks(value))
            if ")" in value:
                open_parent = None
            continue

        cleaned = _clean_fragment(value)
        if cleaned:
            labels.append(cleaned)

    return list(dict.fromkeys(labels))

