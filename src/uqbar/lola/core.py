# SPDX-License-Identifier: MIT
# uqbar/lola/core.py
"""
Lola | Core
===========

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
- Project: Lola
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

from uqbar.lola.todo_maker import todo_generator


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
class Subcommand(Enum):
    """Placeholder"""
    TODO = "todo"


@dataclass
class Args:
    COMMAND_SUBTIPE: str = "command_subtipe"
    DATE_START: str = "date_start"
    DATE_END: str = "date_end"
    OUTPUT_PATH: str = "output_path"



@dataclass
class Semaphore:
    """Placeholder"""
    ZERO: bool = True
    A_ONE: bool = True


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def lola_core(
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
    command_subtipe: str = ""
    date_start: str | None = None
    date_end: str | None = None
    output_path: Path = Path()

    # 0. Setup
    if Semaphore.ZERO:
        command_subtipe: str = args[Args.COMMAND_SUBTIPE]
        date_start: str | None = args[Args.DATE_START]
        date_end: str | None = args[Args.DATE_END]
        output_path: Path = args[Args.OUTPUT_PATH]

    if not command_subtipe:
        return_code = 1
        return return_code

    if not date_start:
        from datetime import date
        date_start = date.today().isoformat()

    if not date_end:
        from datetime import date
        today = date.today()
        date_end = date(today.year, 12, 31).isoformat()

    if not output_path:
        output_path = Path.cwd()

    # A. Youtube Video/Audio Fetch
    if command_subtipe == Subcommand.TODO.value and date_start < date_end:

        # A.1. Youtube Search
        if Semaphore.A_ONE:
            todo_generator(
                start_date_str=date_start,
                end_date_str=date_end,
                output_path=output_path,
            )


    # Return
    return return_code


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "lola_core",
]

# -------------------------------------------------------------------------------------
# Test | python -m uqbar lola todo -s '2026-01-01' -e '2026-12-31' -o '~/Desktop/default.todo'  > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...


