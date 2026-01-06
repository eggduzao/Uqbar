# SPDX-License-Identifier: MIT
# uqbar/tieta/core.py
"""
Tieta | Core
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
- Project: Tieta
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from uqbar.tieta.claude_prompt_parser import create_prompts
from uqbar.tieta.pdf_parser import clean_chunk_string, read_input_pdf

# from uqbar.tieta.utils import read_redflags

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
@dataclass
class Args:
    INPUT_PATH: str = "input_path"
    OUTPUT_PATH: str = "output_path"
    START_PAGE: str = "start_page"
    FINAL_PAGE: str = "final_page"
    REDFLAGS: str = "redflags"
    REDFLAGS_PATH: str = "redflags_path"


@dataclass
class Semaphore:
    """Placeholder"""
    ONE: bool = True
    TWO: bool = False
    THREE: bool = False


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _write_output_txt(
    prompt_text: list[list[str]],
    output_path: Path,
) -> None:
    with open(output_path, "w") as output_file:
        for chunk in prompt_text:
            output_file.write(" ".join(chunk) + "\n")


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def tieta_core(
    args: dict[str, Any],
) -> int:
    """
    Entry point for `python -m tieta` and the console script.

    Parameters
    ----------
    argv : argparse.Namespace
        Parsed arguments.

    Returns
    -------
    return_code : int
        Integer representing the formal exit status.

    Notes
    -----
    Placeholder
    """
    return_code: int = 0

    # 0. Setup
    input_path: Path = Path(args[Args.INPUT_PATH])
    output_path: Path = Path(args[Args.OUTPUT_PATH])
    start_page: int = int(args[Args.START_PAGE])
    final_page: int = int(args[Args.FINAL_PAGE])
    redflags: bool = args[Args.REDFLAGS]
    redflags_path: Path = Path(args[Args.REDFLAGS_PATH])

    # 1. Parsing input PDF
    raw_string_list: list[str] = read_input_pdf(
        input_path=input_path,
        start_page=start_page,
        final_page=final_page,
        redflags=redflags,
        redflags_path=redflags_path,
    )

    clean_chunked_string: list[list[str]] = clean_chunk_string(raw_string_list)

    # 2. Creating Claude prompts
    prompt_text: list[list[str]] = create_prompts(clean_chunked_string)

    # 3. Output to text file
    _write_output_txt(
        prompt_text=prompt_text,
        output_path=output_path,
    )

    # Return
    return return_code

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "tieta_core",
]
