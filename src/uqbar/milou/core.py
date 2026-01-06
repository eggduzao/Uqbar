# SPDX-License-Identifier: MIT
# uqbar/milou/core.py
"""
Milou | Core
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
- Project: Milou
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from uqbar.milou.book_pdf_downloader import download_write, search_for_links
from uqbar.milou.book_processor import (
    form_final_query_list,
    get_search_engine_links,
    parse_query,
    verify_query_formats,
)


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
class Subcommand(Enum):
    """Placeholder"""
    YOUTUBE = "youtube"
    BOOK = "book"


@dataclass
class Args:
    COMMAND_SUBTIPE: str = "command_subtipe"
    INPUT_PATH: str = "input_path"
    OUTPUT_PATH: str = "output_path"
    QUERY: str = "query"
    SEARCH_ENGINES: str = "search_engines"
    FORMATS_ALLOWED: str = "formats_allowed"


@dataclass
class Semaphore:
    """Placeholder"""
    ZERO: bool = True
    A_ONE: bool = False
    A_TWO: bool = False
    A_THREE: bool = False
    A_FOUR: bool = False
    A_FIVE: bool = False
    A_SIX: bool = False
    B_ONE: bool = True
    B_TWO: bool = True
    B_THREE: bool = True
    B_FOUR: bool = True
    B_FIVE: bool = True
    B_SIX: bool = True

# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def milou_core(
    args: dict[str, Any],
) -> int:
    """
    Entry point for `python -m milou` and the console script.

    Parameters
    ----------
    args : dict[str, Any]
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
    if Semaphore.ZERO:
        command_subtipe: str = args[Args.COMMAND_SUBTIPE]
        input_path: Path = args[Args.INPUT_PATH]
        output_path: Path = args[Args.OUTPUT_PATH]
        query: str = args[Args.QUERY]
        search_engines: str = args[Args.SEARCH_ENGINES]
        formats_allowed: str = args[Args.FORMATS_ALLOWED]

    # A. Youtube Video/Audio Fetch
    if command_subtipe == Subcommand.YOUTUBE.value:

        # A.1. Youtube Search
        pass

    # B. Book Search
    elif command_subtipe == Subcommand.BOOK.value:

        # B.1. Parsing input
        if Semaphore.B_ONE:
            query_list: list[str] = parse_query(
                single_query=query,
                input_path=input_path
            )

        # B.2. Get search engines links
        if Semaphore.B_TWO:
            search_engine_links: list[str] = get_search_engine_links(
                search_engines=search_engines,
            )

        # B.3. Verify query formats
        if Semaphore.B_THREE:
            query_format_list: list[str] = verify_query_formats(
                formats_allowed=formats_allowed,
            )

        # B.4. Get final query links
        if Semaphore.B_FOUR:
            final_link_list: list[str] = form_final_query_list(
                query_list=query_list,
                search_engine_list=search_engine_links,
                format_list=query_format_list,
            )

        # B.5. Search for links
        if Semaphore.B_FIVE:
            query_link_list: list[str] = search_for_links(
                link_list=final_link_list,
                query_format_list=query_format_list
            )

        # B.6. Download links to output to directory
        if Semaphore.B_SIX:
            download_write(
                query_link_list=query_link_list,
                output_path=output_path,
                write_dictionary=True,
            )

    # Return
    return return_code

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "milou_core",
]
