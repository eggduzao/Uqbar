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

import functools
import warnings
from datetime import datetime


# --------------------------------------------------------------------------------------
# Early utilities
# --------------------------------------------------------------------------------------
def deprecated(reason: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def dtnow(*, fmt: bool = True):
    if fmt:
        return f"[{str(datetime.now()).split(".")[0]}]"
    return datetime.now()


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "deprecated",
    "dtnow",
]
