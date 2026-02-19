# SPDX-License-Identifier: MIT
# uqbar/utils/utils.py
"""
Uqbar | Utils | Utils
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

import functools
import os
import random
import secrets
import subprocess
import time
import warnings
from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, ParamSpec, TypeVar

# --------------------------------------------------------------------------------------
# Early utilities
# --------------------------------------------------------------------------------------
P = ParamSpec("P")

R = TypeVar("R")


def deprecated(reason: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Mark a function as deprecated.

    Parameters
    ----------
    reason : str
        Explanation of why the function is deprecated and/or what to use instead.

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        A decorator preserving the original function's signature and return type.

    Notes
    -----
    - Emits a ``DeprecationWarning`` at call time.
    - Uses ``stacklevel=2`` so the warning points to the caller.
    - Signature is preserved via ``ParamSpec``.
    - Compatible with Python 3.10+.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def dtnow(*, fmt: bool = True):
    if fmt:
        return f"[{str(datetime.now()).split(".")[0]}]"
    return datetime.now()

def execute(command: str, *, ecapture_output: bool =True, etext: bool =True, echeck: bool =True) -> Any:

    result: Any = None
    try:
        comlist = command.split(" ")
        result = subprocess.run(comlist, capture_output=ecapture_output, text=etext, check=echeck)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stderr: {e.stderr}")

    return result.stdout


def execute_sequential_one_session(command_list: list[str]) -> tuple[str, str]:
    """
    Execute a list of shell commands sequentially in the same session.

    Args:
        command_list: A list of shell commands as strings.

    Returns:
        A tuple (stdout, stderr) containing the combined output and error messages.
    """
    # Join commands with "&&" or ";"
    # "&&" stops execution on failure; ";" executes all regardless
    full_command = " ; ".join(command_list)

    # Run in a single shell session
    process = subprocess.Popen(
        full_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,   # ensures output is returned as str (not bytes)
        executable="/bin/bash"  # force bash for consistency
    )
    stdout, stderr = process.communicate()

    return stdout.strip(), stderr.strip()


def execute_sequential_one_session_strict(
    command_list: list[str],
    *,
    env: Mapping[str, str] | None = None,
    strict: bool = False,
) -> tuple[str, str]:
    """
    Execute commands sequentially in ONE bash process.

    Notes
    -----
    - Variables persist only within this call.
    - Use `export VAR=...` if child processes must see VAR.
    """
    prolog = "set -Eeuo pipefail; " if strict else ""
    full_command = prolog + " ; ".join(command_list)

    proc_env = os.environ.copy()
    if env:
        proc_env.update(env)

    p = subprocess.Popen(
        ["/bin/bash", "-lc", full_command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=proc_env,
    )
    stdout, stderr = p.communicate()
    return stdout.strip(), stderr.strip()


def read_external_file(
    path: Path,
    *,
    trim_all_newlines: bool = False,
    trim_final_newline: bool = True,
) -> list[str]:
    """
    Read a text file containing one or more double-quoted strings and return them.

    Each string:
    - starts with a double quote (")
    - ends with a matching double quote (")
    - may span multiple lines

    Parameters
    ----------
    path : Path
        Path to the input text file.
    trim_all_newlines : bool, default False
        If True, remove ALL '\\n' characters inside each string.
    trim_final_newline : bool, default True
        If True, remove a single trailing '\\n' from each string (if present).

    Returns
    -------
    list[str]
        Extracted strings, without the surrounding quotes.
    """
    text = path.read_text(encoding="utf-8")

    results: list[str] = []
    buf: list[str] = []
    in_string = False

    i = 0
    while i < len(text):
        ch = text[i]

        if ch == '"':
            if in_string:
                # closing quote
                s = "".join(buf)
                buf.clear()
                in_string = False

                if trim_all_newlines:
                    s = s.replace("\n", "")
                elif trim_final_newline and s.endswith("\n"):
                    s = s[:-1]

                results.append(s)
            else:
                # opening quote
                in_string = True
        else:
            if in_string:
                buf.append(ch)

        i += 1

    if in_string:
        raise ValueError("Unclosed string literal detected in file")

    return results


def hyper_random(
    interval: list[Any] | None = None,
    *,
    number: int = 1,
    mode: str = "without"
) -> Any:
    """
    Generate hyper-random values that never repeat with any seed,
    using high-entropy system randomness.

    Parameters
    ----------
    interval : Optional[list[Any]]
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
        - If interval=None: returns int or list[int].
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
# Classes
# --------------------------------------------------------------------------------------
class PassError(Exception):
    pass



# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "deprecated",
    "dtnow",
    "PassError",
]
