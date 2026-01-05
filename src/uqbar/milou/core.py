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

import enum
import argparse
from pathlib import Path

from uqbar.milou.book_preprocessor import (
    parse_query,
    get_search_engine_links,
    form_final_query_list,
    verify_query_formats,
)

from uqbar.milou.book_pdf_downloader import search_for_links, download_write


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
class Subcommand(enum):
    """Placeholder"""
    YOUTUBE: str = "youtube"
    BOOK: str = "book"


@dataclass
class Args:
    COMMAND_SUBTIPE: str | None = "command_subtipe"
    INPUT_PATH: str | None = "input_path"
    OUTPUT_PATH: str | None = "output_path"
    QUERY: str | None = "query"
    SEARCH_ENGINES: str | None = "search_engines"
    FORMATS_ALLOWED: str | None = "formats_allowed"


@dataclass
class Semaphore:
    """Placeholder"""
    ZERO: bool = True
    A_ONE: bool = False
    A_TWO: bool = False
    A_THREE: bool = False
    B_ONE: bool = True
    B_TWO: bool = False
    B_THREE: bool = False
    B_FOUR: bool = False
    B_FIVE: bool = False
    B_SIX: bool = False

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
        command_subtipe: str = args[Subcommand.YOUTUBE]
        input_path: str = args[Args.INPUT_PATH]
        output_path: str = args[Args.OUTPUT_PATH]
        query: str = args[Args.QUERY]
        search_engines: str = args[Args.SEARCH_ENGINES]
        formats_allowed: str = args[Args.FORMATS_ALLOWED]

    # A. Youtube Video/Audio Fetch
    if command_subtipe == Subcommand.YOUTUBE:
        
        # A.1. Youtube Search
        if Semaphore.A_ONE:
            pass

    # B. Book Search
    elif command_subtipe == Subcommand.BOOK:
        
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
            link_list: list[str] = form_final_query_list(
                query_list=query_list,
                search_engine_list=search_engine_links,
            )

        # B.5. Search for links
        if Semaphore.B_FIVE:
            query_link_list: list[str] = search_for_links(
                link_list=link_list,
                query_format_list=query_format_list,
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
