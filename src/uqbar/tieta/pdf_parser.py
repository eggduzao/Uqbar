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

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
@dataclass(slots=True)
class PdfParseWarning:
    kind: str
    page: int | None
    detail: str


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _extract_pdf_text_to_file(
    pdf_path: Path,
    out_txt_path: Path,
    *,
    initial_page: int | None = None,
    final_page: int | None = None,
    min_chars_per_page: int = 30,
    image_heavy_threshold: int = 3,
    warn_on_many_empty_pages_ratio: float = 0.30,
) -> list[PdfParseWarning]:
    """
    Extract text-only from a PDF and write it to a .txt file.

    "Red flag" warnings included:
    - Pages with *very little* extracted text (often scanned pages or weird layout).
    - Pages that contain multiple images but little text (likely scan or heavy diagrams).
    - A high ratio of empty/near-empty pages.
    - PDF encrypted / unreadable errors.

    Returns
    -------
    list[PdfParseWarning]
        Structured warnings you can print/log.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF: {pdf_path}")

    out_txt_path.parent.mkdir(parents=True, exist_ok=True)

    warnings: list[PdfParseWarning] = []
    extracted_pages: list[str] = []

    total_pages = 0
    low_text_pages = 0
    image_heavy_pages = 0

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            total_pages = len(pdf.pages)

            for idx, page in enumerate(pdf.pages, start=1):

                if initial_page is not None and idx < initial_page:
                    continue

                if final_page is not None and idx > final_page:
                    continue

                # Text extraction (ignore images, but we can *count* them for red flags)
                try:
                    text = page.extract_text() or ""
                except Exception as e:
                    warnings.append(PdfParseWarning(
                        kind="page_extract_error",
                        page=idx,
                        detail=f"Failed to extract page text: {e}",
                    ))
                    text = ""

                # Basic “how much text did we get?”
                text_stripped = text.strip()
                if len(text_stripped) < min_chars_per_page:
                    low_text_pages += 1
                    warnings.append(PdfParseWarning(
                        kind="low_text",
                        page=idx,
                        detail=f"Extracted only {len(text_stripped)} chars (< {min_chars_per_page}). "
                               "This page may be scanned, image-based, or layout-heavy.",
                    ))

                # Count images for “scan-ish” detection (still ignore them in output)
                img_count = 0
                try:
                    # page.images is a list of image objects known to pdfplumber
                    img_count = len(page.images or [])
                except Exception:
                    img_count = 0

                if img_count >= image_heavy_threshold and len(text_stripped) < min_chars_per_page:
                    image_heavy_pages += 1
                    warnings.append(PdfParseWarning(
                        kind="image_heavy_low_text",
                        page=idx,
                        detail=f"Page has {img_count} images and very little text. Likely a scan/diagram page.",
                    ))

                # Keep a clean separator between pages for readability
                extracted_pages.append(
                    f"\n\n===== PAGE {idx}/{total_pages} =====\n\n{text_stripped}\n"
                )

    except Exception as e:
        # Encrypted PDFs or corrupted files often fail here
        warnings.append(PdfParseWarning(
            kind="pdf_open_error",
            page=None,
            detail=f"Failed to open/parse PDF: {e}",
        ))

    # Global “many pages are empty” warning
    if total_pages > 0:
        ratio = low_text_pages / total_pages
        if ratio >= warn_on_many_empty_pages_ratio:
            warnings.append(PdfParseWarning(
                kind="many_low_text_pages",
                page=None,
                detail=f"{low_text_pages}/{total_pages} pages had low text "
                       f"({ratio:.0%} >= {warn_on_many_empty_pages_ratio:.0%}). "
                       "This PDF may be scanned or have complex tables/layout.",
            ))

    # Write output even if warnings exist
    out_txt_path.write_text("".join(extracted_pages), encoding="utf-8")

    return warnings


# # --- Example usage ---
# if __name__ == "__main__":
#     pdf_in = Path("/Users/egg/Desktop/inclusive_instructional_design_for_neurodiverse_learners.pdf")
#     txt_out = Path("output.txt")

#     warns = extract_pdf_text_to_file(
#         pdf_in,
#         txt_out,
#         initial_page = 2,
#         final_page = 5,
#     )

#     if warns:
#         print("\nWarnings:")
#         for w in warns:
#             where = f"page {w.page}" if w.page is not None else "document"
#             print(f"- [{w.kind}] ({where}) {w.detail}")
#     else:
#         print("No obvious red flags detected.")


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------

def clean_chunk_string(
    raw_string_list: list[str],
) -> list[list[str]]:
    out: list[list[str]] = []
    return out

def read_input_pdf(
        input_path: Path,
        start_page: int,
        final_page: int | None,
        redflags: bool,
        redflags_path: Path,
) -> list[str]:
    out: list[str] = []
    return out

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "read_input_pdf",
    "clean_chunk_string",
]
