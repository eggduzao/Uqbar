# SPDX-License-Identifier: MIT
# uqbar/faust/utils.py
"""
Faust | Utils
=============

Overview
--------
Placeholder.

Metadata
--------
- Project: Faust
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path

from uqbar.faust.ansi import Ansi, _bold_matches, _maybe_color
from uqbar.faust.constants import OutField


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _rel_dir(base: Path, p: Path) -> str:
    try:
        rel = p.parent.relative_to(base)
        return "." if str(rel) == "" else str(rel)
    except Exception:
        # If base isn't an ancestor, fall back
        return str(p.parent)


def _abs_dir(p: Path) -> str:
    return str(p.parent.resolve())


def _trim_around_match(line: str, match: re.Match[str], span: int) -> str:
    start, end = match.span()
    half = span // 2

    left = max(0, start - half)
    right = min(len(line), end + half)

    chunk = line[left:right]

    if left > 0:
        chunk = "…" + chunk
    if right < len(line):
        chunk = chunk + "…"

    return chunk


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def build_row(
    hit: Hit,
    out_fields: list[OutField],
    colour: bool,
    match_patterns: dict[str, re.Pattern[str]],
) -> list[str]:
    p = hit.path
    base = hit.base
    line = hit.line
    fileline = hit.fileline

    dir_major = _maybe_color(_rel_dir(base, p), Ansi.BLUE, colour)
    file_minor = _maybe_color(p.name, Ansi.CYAN, colour)

    # For match bolding, we bold the matched query's pattern inside relevant text columns
    pat = match_patterns[hit.query]

    def fmt_field(field: OutField) -> str:
        if field == "absdir":
            return _maybe_color(_abs_dir(p), Ansi.BLUE, colour)
        if field == "reldir":
            return dir_major
        if field == "filename":
            return file_minor if p.is_file() else "."
        if field == "fileline":
            return str(fileline) if fileline is not None else "."
        if field == "fullline":
            if line is None:
                return "."
            return _bold_matches(line, pat, colour)
        if field in ("trim50", "trim100", "trim250"):
            if line is None:
                return "."
            m = pat.search(line)
            if m is None:
                # should not happen, but be safe
                return _bold_matches(line[:50], pat, colour) if field == "trim50" else _bold_matches(line, pat, colour)
            span = 50 if field == "trim50" else 100 if field == "trim100" else 250
            chunk = _trim_around_match(line, m, span)
            return _bold_matches(chunk, pat, colour)

        return "."

    return [fmt_field(f) for f in out_fields]


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "build_row",
]
