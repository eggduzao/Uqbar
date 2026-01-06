# SPDX-License-Identifier: MIT
# uqbar/_version.py
"""
Uqbar MultiTool | Version
=========================

Overview
--------
Placeholder.

Metadata
--------
- Project: Uqbar
- License: MIT
"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
FILENAME = "VERSION"


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def version() -> str:

    version: str = ""

    file_name: Path = Path(__file__).resolve().parent
    file_name: Path = file_name.parent.parent / FILENAME
    file_name.resolve()
    with open(file_name, encoding="utf-8") as file:

        version = file.read()
        version.strip()

    return version


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "version",
]
