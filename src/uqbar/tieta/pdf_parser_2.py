# SPDX-License-Identifier: MIT
# uqbar/tieta/pdf_parser.py
"""
Tieta | PDF Parser
==================

Overview
--------
Placeholder.

Metadata
--------
- Project: Tieta
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
@dataclass(frozen=True)
class ChapterSlice:
    """Page range to extract (0-indexed, inclusive start, exclusive end)."""
    start_page: int
    end_page_exclusive: int
    reason: str


def extract_first_chapter_pdf(
    *,
    pdf_path: Path,
    output_path: Path,
    # Heuristic knobs (safe defaults)
    max_front_pages_to_scan: int = 100,
    # What "chapter 1" might look like in text/bookmarks/TOC
    chapter1_patterns: tuple[str, ...] = (
        r"\bchapter\s*1\b",
        r"\bcap[ií]tulo\s*1\b",      # Portuguese-friendly
        r"\b1\s*[\.\-:]\s",          # "1. " / "1 - " etc (weak signal)
        r"\bintroduction\b",         # many books put first chapter as "Introduction"
        r"\bintrodu[cç][aã]o\b",
    ),
    # What "chapter 2" might look like (used to determine where ch1 ends)
    chapter2_patterns: tuple[str, ...] = (
        r"\bchapter\s*2\b",
        r"\bcap[ií]tulo\s*2\b",
        r"\b2\s*[\.\-:]\s",
    ),
) -> ChapterSlice:
    """
    Extract the "first chapter" of a PDF into a new PDF.

    Core idea (most generalized):
    1) If the PDF has an outline/bookmarks, use it to locate Chapter 1 and the next chapter.
    2) Else, try to infer chapter start/end from a Table-of-Contents page (by reading text).
    3) Else, scan first pages for Chapter 1 / Chapter 2 headings and slice accordingly.

    Returns:
        ChapterSlice with the chosen page range (0-indexed) and a reason string.

    Requirements:
        pip install pypdf

    Notes:
        - Page numbers inside a PDF are often roman numerals / logical pages; we operate on
          actual page indices (0..N-1).
        - “Text extraction” from PDFs is heuristic by nature; this works best on born-digital PDFs.
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {pdf_path.name}")

    reader: PdfReader = PdfReader(str(pdf_path))
    n_pages: int = len(reader.pages)
    print(n_pages)
    if n_pages == 0:
        raise ValueError("PDF has 0 pages.")

    # Compile regex once (fast and consistent)
    ch1_re = re.compile("|".join(f"(?:{p})" for p in chapter1_patterns), flags=re.IGNORECASE)
    ch2_re = re.compile("|".join(f"(?:{p})" for p in chapter2_patterns), flags=re.IGNORECASE)

    # ---------------------------------------------------------------------
    # Strategy 1: Use bookmarks / outline (highest-quality when available)
    # ---------------------------------------------------------------------

    def _flatten_outline(outline: Any) -> list[Any]:
        """
        Outline can be a nested list of destinations / dicts / etc.
        We flatten it into a list of “items” we can inspect.
        """
        flat: list[Any] = []

        def walk(node: Any) -> None:
            if node is None:
                return
            if isinstance(node, list):
                for x in node:
                    walk(x)
                return
            # Some outline items are dict-like; some are Destination objects.
            flat.append(node)
            # Many outline nodes have .children or are followed by nested lists.
            children = getattr(node, "children", None)
            if children:
                walk(children)

        walk(outline)
        return flat

    def _outline_title(item: Any) -> str:
        """
        Attempt to retrieve the title text shown in bookmarks.
        pypdf typically uses Destination.title.
        """
        t = getattr(item, "title", None)
        if isinstance(t, str) and t.strip():
            return t.strip()
        # Sometimes outline items come as dicts
        if isinstance(item, dict):
            for k in ("title", "/Title"):
                v = item.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()
        return ""

    def _outline_page_index(item: Any) -> int | None:
        """
        Convert an outline destination into a 0-indexed page number.
        """
        try:
            # pypdf has get_destination_page_number for Destination-like objects
            return reader.get_destination_page_number(item)
        except Exception:
            # Some items might not be destinations or might be malformed
            return None

    # Try outline extraction
    outline = None
    try:
        outline = reader.outline  # pypdf >= 3 tends to use `.outline`
    except Exception:
        try:
            outline = reader.outlines  # older naming
        except Exception:
            outline = None

    if outline:
        flat = _flatten_outline(outline)
        # Collect candidates: (page_idx, title)
        entries: list[tuple[int, str]] = []
        for item in flat:
            title = _outline_title(item)
            if not title:
                continue
            page_idx = _outline_page_index(item)
            if page_idx is None:
                continue
            entries.append((page_idx, title))

        # Sort by page index so we can find "next chapter" reliably
        entries.sort(key=lambda x: x[0])

        # Find first entry that looks like Chapter 1 (or "Introduction" etc.)
        ch1_candidates = [(p, t) for (p, t) in entries if ch1_re.search(t)]
        if ch1_candidates:
            ch1_start = ch1_candidates[0][0]

            # End is next outline item that looks like Chapter 2 (preferred)
            ch2_candidates = [(p, t) for (p, t) in entries if p > ch1_start and ch2_re.search(t)]
            if ch2_candidates:
                ch1_end = ch2_candidates[0][0]
                slice_ = ChapterSlice(ch1_start, ch1_end, "outline: chapter1 -> chapter2")
                _write_pdf_slice(reader, output_path, slice_)
                return slice_

            # If no clear Chapter 2, end at next outline entry after Chapter 1 start
            next_after = [(p, t) for (p, t) in entries if p > ch1_start]
            if next_after:
                ch1_end = next_after[0][0]
                slice_ = ChapterSlice(ch1_start, ch1_end, "outline: chapter1 -> next outline entry")
                _write_pdf_slice(reader, output_path, slice_)
                return slice_

            # If Chapter 1 is last outline entry, take until end
            slice_ = ChapterSlice(ch1_start, n_pages, "outline: chapter1 -> end of document")
            _write_pdf_slice(reader, output_path, slice_)
            return slice_

    # ---------------------------------------------------------------------
    # Strategy 2: Try to infer from a Table of Contents (TOC) page
    # ---------------------------------------------------------------------
    #
    # Idea:
    # - Many PDFs have a “Contents” / “Sumário” page early on.
    # - If we can find it, we try to read lines like:
    #       Chapter 1 ....... 5
    #       Chapter 2 ....... 19
    # - Then we convert those printed numbers into an *approximate* page index.
    #
    # Caveat:
    # - Printed page numbers may not match PDF page indices (front matter in roman numerals).
    # - So we treat TOC numbers as hints and validate them by scanning around.

    def _page_text(i: int) -> str:
        try:
            t = reader.pages[i].extract_text() or ""
        except Exception:
            return ""
        return t

    toc_page_idx = None
    toc_re = re.compile(r"\b(contents|table of contents|sum[aá]rio)\b", flags=re.IGNORECASE)

    for i in range(min(max_front_pages_to_scan, n_pages)):
        if toc_re.search(_page_text(i)):
            toc_page_idx = i
            break

    if toc_page_idx is not None:
        toc_text = _page_text(toc_page_idx)
        # Extremely forgiving line parser: look for "chapter 1 ... <number>"
        # We accept numbers at end of line.
        lines = [ln.strip() for ln in toc_text.splitlines() if ln.strip()]
        ch1_num = None
        ch2_num = None

        # Find the first line that matches chapter1_patterns AND ends with a number
        endnum_re = re.compile(r"(\d{1,4})\s*$")
        for ln in lines:
            m_num = endnum_re.search(ln)
            if not m_num:
                continue
            if ch1_re.search(ln):
                ch1_num = int(m_num.group(1))
                break

        if ch1_num is not None:
            # Find a plausible chapter 2 page number
            for ln in lines:
                m_num = endnum_re.search(ln)
                if not m_num:
                    continue
                if ch2_re.search(ln):
                    ch2_num = int(m_num.group(1))
                    break

            # Convert those printed numbers to *approximate* PDF indices by searching around.
            # We guess the PDF page index where Chapter 1 heading actually appears.
            ch1_start = _find_heading_near_printed_page(
                reader=reader,
                printed_page=ch1_num,
                heading_re=ch1_re,
                search_radius=12,
            )

            if ch1_start is not None:
                if ch2_num is not None:
                    ch1_end = _find_heading_near_printed_page(
                        reader=reader,
                        printed_page=ch2_num,
                        heading_re=ch2_re,
                        search_radius=12,
                    )
                    if ch1_end is not None and ch1_end > ch1_start:
                        slice_ = ChapterSlice(ch1_start, ch1_end, "toc: validated chapter1 -> chapter2")
                        _write_pdf_slice(reader, output_path, slice_)
                        return slice_

                # If no validated Chapter 2, end at next detected Chapter 2 heading by scanning forward
                ch1_end = _scan_forward_for_heading(reader, start=ch1_start + 1, heading_re=ch2_re, limit=200)
                if ch1_end is not None:
                    slice_ = ChapterSlice(ch1_start, ch1_end, "toc: validated chapter1 -> first chapter2 heading scan")
                    _write_pdf_slice(reader, output_path, slice_)
                    return slice_

                # Fallback: take a conservative chunk (e.g., 30 pages) if nothing else
                slice_ = ChapterSlice(ch1_start, min(ch1_start + 30, n_pages), "toc: validated chapter1 -> conservative 30-page slice")
                _write_pdf_slice(reader, output_path, slice_)
                return slice_

    # ---------------------------------------------------------------------
    # Strategy 3: Brutal fallback — scan the first N pages for headings
    # ---------------------------------------------------------------------
    #
    # This is “best effort”: we assume chapter headings literally appear in text extraction.
    # Works decently for born-digital PDFs; may fail for scans or fancy typography.

    ch1_start = _scan_forward_for_heading(reader, start=0, heading_re=ch1_re, limit=max_front_pages_to_scan)
    if ch1_start is None:
        # Last-resort: assume first chapter begins at page 0 (some books do)
        ch1_start = 0

    ch1_end = _scan_forward_for_heading(reader, start=ch1_start + 1, heading_re=ch2_re, limit=min(n_pages, ch1_start + 250))
    if ch1_end is None:
        # Conservative fallback if Chapter 2 not found
        ch1_end = min(ch1_start + 30, n_pages)

    slice_ = ChapterSlice(ch1_start, ch1_end, "fallback: heading scan / conservative slice")
    _write_pdf_slice(reader, output_path, slice_)
    return slice_


# ----------------------------
# Helper functions (explained)
# ----------------------------

def _write_pdf_slice(reader: PdfReader, output_path: Path, slice_: ChapterSlice) -> None:
    """
    Writes a new PDF consisting only of pages [start_page, end_page_exclusive).
    This part is *easy* in PDF-land: splitting by pages is reliable.
    """
    start = max(0, slice_.start_page)
    end = min(len(reader.pages), slice_.end_page_exclusive)
    if end <= start:
        raise ValueError(f"Invalid slice: {slice_}")

    writer = PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        writer.write(f)


def _scan_forward_for_heading(
    reader: PdfReader,
    *,
    start: int,
    heading_re: re.Pattern[str],
    limit: int,
) -> int | None:
    """
    Scan pages from `start` up to `limit` pages (absolute page cap),
    returning the first page index whose extracted text matches heading_re.

    Why this works:
    - Many born-digital PDFs include real text.
    Why it fails:
    - Scanned PDFs (images) => no text unless OCR.
    - Some PDFs encode text in weird ways; extraction returns scrambled order.
    """
    n_pages = len(reader.pages)
    end = min(n_pages, limit) if limit >= 0 else n_pages

    for i in range(max(0, start), end):
        try:
            text = reader.pages[i].extract_text() or ""
        except Exception:
            continue
        if heading_re.search(text):
            return i
    return None


def _find_heading_near_printed_page(
    *,
    reader: PdfReader,
    printed_page: int,
    heading_re: re.Pattern[str],
    search_radius: int = 10,
) -> int | None:
    """
    Given a printed page number from the TOC (e.g., "Chapter 1 ... 5"),
    attempt to find the actual PDF page index around that area.

    Key problem:
    - printed page numbers are *document logical pages*
    - PDF page indices include front matter pages, covers, etc.

    So we:
    - treat `printed_page` as a hint
    - search a window of +/- `search_radius` around a guessed index

    Guessing rule (rough but usable):
    - assume printed pages start around PDF index 0
    - so printed_page N maps to pdf index ~ (N - 1)
    - then validate by searching nearby for the actual heading text
    """
    n_pages = len(reader.pages)

    # Naive mapping: printed page 1 -> pdf index 0
    guess = max(0, min(n_pages - 1, printed_page - 1))

    lo = max(0, guess - search_radius)
    hi = min(n_pages, guess + search_radius + 1)

    for i in range(lo, hi):
        try:
            text = reader.pages[i].extract_text() or ""
        except Exception:
            continue
        if heading_re.search(text):
            return i
    return None


# python pdf_test.py > out.txt 2>&1
if __name__ == "__main__":

    from pathlib import Path

    root = Path("/Users/egg/Desktop")

    input_path = root / "books" / "bioinformatics_the_machine_learning_approach_2ed_pierre_baldi_soren_brunak.pdf"
    output_path = root / "chapter1.pdf"

    slice_ = extract_first_chapter_pdf(
        pdf_path=input_path,
        output_path=output_path,
    )
    print(slice_)

