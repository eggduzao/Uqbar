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

import sys
from argparse import ArgumentError
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from uqbar.tieta.claude_prompt_parser import create_prompts
from uqbar.tieta.gpt_prompt_parser import create_multiprompt_list
from uqbar.tieta.pdf_parser import clean_chunk_string, read_input_pdf


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
class Subcommand(Enum):
    """Placeholder"""
    CLAUDE = "claude"
    GPT = "gpt"


@dataclass
class Args:
    COMMAND_SUBTIPE: str = "command_subtipe"
    INPUT_PATH: str = "input_path"
    INPUT_PATH_LIST: str = "input_path_list"
    OUTPUT_PATH: str = "output_path"
    START_PAGE: str = "start_page"
    FINAL_PAGE: str = "final_page"
    REDFLAGS: str = "redflags"
    REDFLAGS_PATH: str = "redflags_path"


@dataclass
class Semaphore:
    """Placeholder"""
    ZERO = True
    CLAUDE_ONE: bool = False
    CLAUDE_TWO: bool = False
    CLAUDE_THREE: bool = False
    GPT_ONE: bool = True
    GPT_TWO: bool = True


# Rulers
BIG_RULER_LEN: int = 170

SMALL_RULER_LEN: int = 25


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


def _write_prompt_txt(
    prompt_list: list[str],
    output_path: Path,
) -> None:

    with open(output_path, "w") as output_file:

        total_count: int = len(prompt_list)

        for counter, prompt_str in enumerate(prompt_list, start = 1):


            first_ruler: str = f"{'-'*BIG_RULER_LEN}\n\n"
            last_ruler: str = "\n"
            final_prompt: str = (
                f"{first_ruler}"
                f"> INTERESTING TOPICS MULTIPROMPT [{counter:02d} of {total_count:02d}]\n"
                f"\n"
                f"{prompt_str}\n"
                f"\n"
                f"{'-'*SMALL_RULER_LEN}\n"
                f"\n"
                f"XXXXX\n"
                f"{last_ruler}"
            )

            output_file.write(final_prompt)

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
    command_subtipe: str = ""
    input_path: Path | None = None
    input_path_list: list[Path] | None = None
    output_path: Path | None = None
    start_page: int | None = None
    final_page: int | None = None
    redflags: bool = False
    redflags_path: Path | None = None

    # 0. Setup
    if Semaphore.ZERO:

        command_subtipe = args[Args.COMMAND_SUBTIPE]

        if args[Args.INPUT_PATH]:
            input_path = Path(args[Args.INPUT_PATH])

        if args[Args.INPUT_PATH_LIST]:
            input_path_list = args[Args.INPUT_PATH_LIST]

        if not input_path and not input_path_list:
            raise ArgumentError(sys.exit(0), "At least one input method should be used")

        if args[Args.OUTPUT_PATH]:
            output_path = Path(args[Args.OUTPUT_PATH])
        else:
            raise ArgumentError(sys.exit(0), "At least one output method should be used")

        if args[Args.START_PAGE]:
            start_page = int(args[Args.START_PAGE])
        else:
            start_page = 1

        if args[Args.FINAL_PAGE]:
            final_page = int(args[Args.FINAL_PAGE])
        else:
            final_page = 2

        if Args.REDFLAGS:
            redflags = args[Args.REDFLAGS]

        if args[Args.REDFLAGS_PATH]:
            redflags_path = Path(args[Args.REDFLAGS_PATH])

    # Check subcommand - Claude
    if command_subtipe == Subcommand.CLAUDE.value:

        raw_string_list: list[str] = []
        clean_chunked_string: list[list[str]] = []
        prompt_text: list[list[str]] = []

        # 1. Parsing input PDF
        if Semaphore.CLAUDE_ONE:
            raw_string_list: list[str] = read_input_pdf(
                input_path=input_path,
                start_page=start_page,
                final_page=final_page,
                redflags=redflags,
                redflags_path=redflags_path,
            )

        # 2. Creating Claude prompts
        if Semaphore.CLAUDE_TWO:
            clean_chunked_string: list[list[str]] = clean_chunk_string(
                raw_string_list=raw_string_list,
            )
            prompt_text: list[list[str]] = create_prompts(
                clean_chunked_string=clean_chunked_string,
            )

        # 3. Output to text file
        if Semaphore.CLAUDE_THREE:
            _write_output_txt(
                prompt_text=prompt_text,
                output_path=output_path,
            )

    # Check subcommand - GPT
    if command_subtipe == Subcommand.GPT.value:

        multiprompt_list: list[str] = []

        # 1. Creating GPT Multiprompt
        if Semaphore.GPT_ONE:
            multiprompt_list = create_multiprompt_list(
                input_path_list=input_path_list,
            )

        # 2. Output prompt to text file
        if Semaphore.GPT_TWO:
            _write_prompt_txt(
                prompt_list=multiprompt_list,
                output_path=output_path,
            )

    # Return
    return return_code



# Example:
# pathloc='/Users/egg/Desktop/zo_old,/Users/egg/Desktop/zo_projects,/Users/egg/Desktop/zo_subjects'
# python -m uqbar tieta gpt -l $pathloc -o topics_prompt.txt > out.txt 2>&1
# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "tieta_core",
]
