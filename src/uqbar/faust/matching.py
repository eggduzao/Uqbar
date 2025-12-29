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

from dataclasses import dataclass
from datetime import datetime
import re
import stat
from typing import Iterable

from uqbar.faust.constants import SearchType
from uqbar.faust.io import build_row


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _any_match(patterns: list[re.Pattern[str]], text: str) -> re.Pattern[str] | None:
    for p in patterns:
        if p.search(text):
            return p
    return None


def _is_probably_binary(chunk: bytes) -> bool:
    # heuristic: NUL bytes in first chunk => treat as binary
    return b"\x00" in chunk


def _format_mtime(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _get_metadata_line(p: Path) -> str:
    st = p.stat()
    mode = stat.filemode(st.st_mode)
    size = st.st_size
    mtime = _format_mtime(st.st_mtime)
    return f"mode={mode} size={size} mtime={mtime}"


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def search_dirnames(
    targets: Iterable[Path],
    base: Path,
    patterns: list[re.Pattern[str]],
    raw_queries: list[str],
) -> Iterable[Hit]:
    for p in targets:
        if p.is_dir():
            name = p.name
            pat = _any_match(patterns, name)
            if pat is None:
                continue
            q = raw_queries[patterns.index(pat)]
            yield Hit(base=base, path=p, kind="dir", query=q, fileline=None, line=None)


def search_filenames(
    targets: Iterable[Path],
    base: Path,
    patterns: list[re.Pattern[str]],
    raw_queries: list[str],
) -> Iterable[Hit]:
    for p in targets:
        if p.is_file():
            name = p.name
            pat = _any_match(patterns, name)
            if pat is None:
                continue
            q = raw_queries[patterns.index(pat)]
            yield Hit(base=base, path=p, kind="file", query=q, fileline=None, line=None)


def search_content(
    targets: Iterable[Path],
    base: Path,
    patterns: list[re.Pattern[str]],
    raw_queries: list[str],
) -> Iterable[Hit]:
    for p in targets:
        if not p.is_file():
            continue

        try:
            with p.open("rb") as bf:
                head = bf.read(2048)
                if _is_probably_binary(head):
                    continue
        except OSError:
            continue

        try:
            with p.open("r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, start=1):
                    line_nl = line.rstrip("\n")
                    pat = _any_match(patterns, line_nl)
                    if pat is None:
                        continue
                    q = raw_queries[patterns.index(pat)]
                    yield Hit(base=base, path=p, kind="content", query=q, fileline=i, line=line_nl)
        except OSError:
            continue


def search_metadata(
    targets: Iterable[Path],
    base: Path,
    patterns: list[re.Pattern[str]],
    raw_queries: list[str],
) -> Iterable[Hit]:
    for p in targets:
        try:
            meta = _get_metadata_line(p)
        except OSError:
            continue

        pat = _any_match(patterns, meta)
        if pat is None:
            continue
        q = raw_queries[patterns.index(pat)]
        yield Hit(base=base, path=p, kind="metadata", query=q, fileline=None, line=meta)


# --------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Hit:
    base: Path
    path: Path
    kind: SearchType
    query: str
    fileline: int | None
    line: str | None


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "search_dirnames",
    "search_filenames",
    "search_content",
    "search_metadata",
    "Hit",
]
