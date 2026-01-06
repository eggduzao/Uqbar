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

from typing import Literal

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
SearchType = Literal["dir", "file", "content", "metadata"]
OutField = Literal[
    "absdir",
    "reldir",
    "filename",
    "fileline",
    "fullline",
    "trim50",
    "trim100",
    "trim250",
]


DEFAULT_TYPES: list[SearchType] = ["content"]
DEFAULT_OUT: list[OutField] = ["reldir", "filename", "fileline", "trim50"]


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "SearchType",
    "OutField",
    "DEFAULT_TYPES",
    "DEFAULT_OUT",
]
