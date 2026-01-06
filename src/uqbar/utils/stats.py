# SPDX-License-Identifier: MIT
# uqbar/utils/stats.py
"""
Uqbar | Utils | Stats
=====================

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

import os
import random
import secrets
import time
from collections.abc import Generator
from typing import Any

import numpy as np

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
NORMAL_GENERATOR: Generator = np.random.default_rng()

NORMAL_MEAN: float = 0.5

NORMAL_STD: float = 0.3

NORMAL_SIZE: float = 1


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------




# -------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------
def get_random(
    *,
    mean: float = NORMAL_MEAN,
    std: float = NORMAL_STD,
    size: float = NORMAL_SIZE,
) -> float:
    """
    Placeholder
    """
    value = NORMAL_GENERATOR.normal(loc = mean, scale = std, size = size)
    return max(float(value[0]), 0.0011)


def hyper_random(
    *,
    interval: list[Any] | None = None,
    number: int = 1,
    mode: str = "without"
) -> Any:
    """
    Generate hyper-random values that never repeat with any seed,
    using high-entropy system randomness.

    Parameters
    ----------
    interval : Optional[List[Any]]
        - If None: return random integers (unbounded).
        - If a list of length == 2 and both elements are ints:
              interpreted as an integer range (closed interval).
        - If a list of arbitrary objects:
              sample from this list. If `number == 1`, returns a single object.
              If `number > 1`, returns a list of objects.
              Sampling respects `mode` ("with" or "without" replacement).

    number : int
        Number of values to return. If 1 -> return a single object.
        If >1 -> return a list.

    mode : str
        "without": sample without replacement.
        "with": sample with replacement.
        Ignored if `interval` is a numerical 2-int range.

    Returns
    -------
    Any
        - A single object or list of objects depending on `number`.
        - If interval=None: returns int or List[int].
        - If interval=[a,b] w/ ints: integer(s) in [a, b].
        - If interval is a list of objects: random selections from that list.

    Notes
    -----
    - Randomness is cryptographically strong: random.seed() is *not* used for
      primary entropy. All draws use secrets.randbelow().
    - Edge cases:
        - interval=[]: raises ValueError.
        - interval=[obj]: only one object exists -> returned always.
        - number > len(interval) with mode="without": raises ValueError.
    """

    # ----------------------------------------
    # SEED ENTROPY: chaotic, non-repeatable
    # ----------------------------------------
    # This affects *ONLY* fallback random module usage.
    # The real entropy comes from `secrets`, but this helps avoid predictability.
    seed_material = (
        secrets.randbits(256)
        ^ int(time.time_ns())
        ^ os.getpid()
        ^ id(object())  # even more entropy from object memory identity
    )
    random.seed(seed_material)

    # -------------------------------------------------------
    # CASE 1 — No interval passed → return hyper-random ints
    # -------------------------------------------------------
    if interval is None:
        if number == 1:
            return secrets.randbits(64)
        return [secrets.randbits(64) for _ in range(number)]

    # -------------------------------------------------------
    # CASE 2 — interval is a 2-int numeric range
    # -------------------------------------------------------
    if (
        isinstance(interval, list)
        and len(interval) == 2
        and all(isinstance(i, int) for i in interval)
    ):
        a, b = interval
        if a > b:
            a, b = b, a  # fix reversed interval

        # secrets.randbelow is [0, n), so we do a shift:
        if number == 1:
            return a + secrets.randbelow(b - a + 1)
        return [a + secrets.randbelow(b - a + 1) for _ in range(number)]

    # -------------------------------------------------------
    # CASE 3 — interval is a list of arbitrary objects
    # -------------------------------------------------------
    if not isinstance(interval, list):
        raise TypeError("`interval` must be a list or None.")

    if len(interval) == 0:
        raise ValueError("`interval` cannot be an empty list.")

    # Only one element → always return it
    if len(interval) == 1:
        return interval[0] if number == 1 else [interval[0]] * number

    # --- Sampling mode ---
    if mode not in ("with", "without"):
        raise ValueError("mode must be either 'with' or 'without'.")

    # WITHOUT replacement
    if mode == "without":
        if number > len(interval):
            raise ValueError(
                f"Cannot sample {number} unique values from "
                f"a list of size {len(interval)}."
            )
        # Use secrets for cryptographically strong shuffle-selection
        shuffled = interval.copy()
        for i in range(len(shuffled) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        result = shuffled[:number]
        return result[0] if number == 1 else result

    # WITH replacement
    else:
        def pick_one():
            return interval[secrets.randbelow(len(interval))]

        if number == 1:
            return pick_one()
        return [pick_one() for _ in range(number)]


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "get_random",
    "hyper_random",
]
