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

# import functools
import os
import re
import sys


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _maybe_color(s: str, code: str, enabled: bool) -> str:
    if not enabled:
        return s
    return f"{code}{s}{Ansi.RESET}"


def _bold_matches(text: str, pattern: re.Pattern[str], enabled: bool) -> str:
    if not enabled:
        return text

    def repl(m: re.Match[str]) -> str:
        return f"{Ansi.BOLD}{m.group(0)}{Ansi.RESET}"

    return pattern.sub(repl, text)


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def supports_ansi() -> bool:
    if not sys.stdout.isatty():
        return False
    term = os.getenv("TERM", "")
    if term in ("dumb", ""):
        return False
    return True


# --------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------
class Ansi:
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"

    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    MAGENTA = "\x1b[35m"
    DIM = "\x1b[2m"


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "_maybe_color",
    "_bold_matches",
    "supports_ansi",
    "Ansi",
]
