# SPDX-License-Identifier: MIT
# uqbar/faust/core.py
"""
Faust | Core
============

Overview
--------
Placeholder.

Usage
-----
Placeholder.

Usage Details
-------------
Placeholder.

Metadata
--------
- Project: Faust
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import fnmatch
from pathlib import Path
import re
import sys
from typing import Iterable

from uqbar.faust.ansi import supports_ansi
from uqbar.faust.constants import SearchType, OutField, DEFAULT_TYPES, DEFAULT_OUT
from uqbar.faust.io import build_row
from uqbar.faust.matching import (
    search_dirnames,
    search_filenames,
    search_content,
    search_metadata,
    Hit,
)


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
ALLOWED_TYPE_LIST: list[str] = ["dir", "file", "content", "metadata"]

ALLOWED_OUTPUT_LIST: list[str] = [
    "absdir", "reldir", "filename", "fileline", 
    "fullline", "trim50", "trim100", "trim250"
]


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _compile_query(q: str) -> re.Pattern[str]:
    """
    Interpret q as:
    - regex if it looks like /.../ or r:...
    - otherwise wildcard via fnmatch translated to regex
    Case-sensitive by default (senior default: do not guess intent).
    """
    q = q.strip()
    if not q:
        raise ValueError("Empty search string is not allowed.")

    if (len(q) >= 2 and q[0] == "/" and q[-1] == "/") or q.startswith("r:"):
        raw = q[1:-1] if (q[0] == "/" and q[-1] == "/") else q[2:]
        return re.compile(raw)

    # wildcard -> regex
    # fnmatch.translate returns a regex that matches the *entire* string; we want search within line,
    # so we remove the \Z anchor and wrap to allow substring search.
    rx = fnmatch.translate(q)
    # rx looks like: (?s:...)\Z
    rx = rx.replace(r"\Z", "")
    return re.compile(rx)


def _iter_targets(locations: list[Path], recursive: bool) -> Iterable[Path]:
    for loc in locations:
        if not loc.exists():
            continue
        if loc.is_file():
            yield loc
            continue

        if not recursive:
            # only immediate children
            for child in loc.iterdir():
                yield child
        else:
            yield loc
            for p in loc.rglob("*"):
                yield p


def _expand_types(raw: list[str] | None) -> list[SearchType]:
    if not raw:
        return DEFAULT_TYPES

    expanded: list[str] = []

    for tok in raw:
        tok = tok.strip()
        if not tok:
            continue
        # wildcard expand against allowed
        if any(ch in tok for ch in "*?[]"):
            expanded.extend([a for a in ALLOWED_TYPE_LIST if fnmatch.fnmatch(a, tok)])
        else:
            expanded.append(tok)

    # de-dupe preserving order
    out: list[SearchType] = []
    for x in expanded:
        if x in ALLOWED_TYPE_LIST and x not in out:
            out.append(x)  # type: ignore[arg-type]

    return out if out else DEFAULT_TYPES


def _expand_outputs(raw: list[str] | None) -> list[OutField]:
    if not raw:
        return DEFAULT_OUT

    expanded: list[str] = []
    for tok in raw:
        tok = tok.strip()
        if not tok:
            continue
        if any(ch in tok for ch in "*?[]"):
            expanded.extend([a for a in ALLOWED_OUTPUT_LIST if fnmatch.fnmatch(a, tok)])
        else:
            expanded.append(tok)

    out: list[OutField] = []
    for x in expanded:
        if x in ALLOWED_OUTPUT_LIST and x not in out:
            out.append(x)  # type: ignore[arg-type]

    return out if out else DEFAULT_OUT


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def faust_core(args: dict[str, Any]) -> int:
    """
    Placeholder
    """
    locations_raw = args["location"] if args["location"] is not None else []
    if not locations_raw:
        locations = [Path.cwd()]
    else:
        locations = [Path(x).expanduser() for x in locations_raw]

    recursive: bool = bool(args["recursive"])
    types: list[SearchType] = _expand_types(args["type"])
    outputs: list[OutField] = _expand_outputs(args["output"])

    raw_queries: list[str] = list(args["string"])
    patterns: list[re.Pattern[str]] = [_compile_query(q) for q in raw_queries]
    match_patterns = {q: p for q, p in zip(raw_queries, patterns, strict=True)}

    colour = bool(args["colour"]) and supports_ansi()

    # Header
    sys.stdout.write("\t".join(outputs) + "\n")

    for loc in locations:
        base = loc if loc.is_dir() else loc.parent
        targets = _iter_targets([loc], recursive)

        hits: list[Hit] = []

        if "dir" in types:
            hits.extend(search_dirnames(targets=_iter_targets([loc], recursive), base=base, patterns=patterns, raw_queries=raw_queries))
        if "file" in types:
            hits.extend(search_filenames(targets=_iter_targets([loc], recursive), base=base, patterns=patterns, raw_queries=raw_queries))
        if "content" in types:
            hits.extend(search_content(targets=_iter_targets([loc], recursive), base=base, patterns=patterns, raw_queries=raw_queries))
        if "metadata" in types:
            hits.extend(search_metadata(targets=_iter_targets([loc], recursive), base=base, patterns=patterns, raw_queries=raw_queries))

        # Print TSV rows
        for hit in hits:
            row = build_row(hit, outputs, colour, match_patterns)
            sys.stdout.write("\t".join(row) + "\n")

    return 0


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "faust_core",
]

# -------------------------------------------------------------------------------------
# Test | python -m uqbar faust -h > out.txt 2>&1
# python -m uqbar faust -l ~/Projects/organization/*.txt -t content -s ACCOUNT -c  > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...


