# SPDX-License-Identifier: MIT
# uqbar/default/core.py
"""
Default | Core
==============

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
- Project: Default
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import argparse
from pathlib import Path


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def default_core(
    argv: argparse.Namespace,
) -> int:
    """
    Entry point for `python -m default` and the console script.

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
    return return_code

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "default_core",
]

# -------------------------------------------------------------------------------------
# Test | python -m uqbar.default.core > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     ...


