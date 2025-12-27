# SPDX-License-Identifier: MIT
# uqbar/cli.py
"""
Uqbar MultiTool | CLI
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

import argparse
from pathlib import Path
from typing import Any, Sequence


from uqbar._version import version

from uqbar.acta.core import acta_core
from uqbar.milou.core import milou_core
from uqbar.quincas.core import quincas_core

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
__version__: str = version()


ACTA: str = "acta"  # Program to generate youtube videos automatically

MILOU: str = "milou"  # Program to mass download youtube vides seamlessly

QUINCAS: str = "quincas"  # Program to produce music effortlesly without DAWs


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _parse_bool(value: str) -> bool:
    """
    Robust boolean parser for CLI strings.

    Accepts common true/false spellings:
    - true/false, t/f, yes/no, y/n, 1/0, on/off

    Raises argparse.ArgumentTypeError on invalid values.
    """
    v = value.strip().lower()
    if v in {"true", "t", "yes", "y", "1", "on"}:
        return True
    if v in {"false", "f", "no", "n", "0", "off"}:
        return False
    raise argparse.ArgumentTypeError(
        f"Invalid boolean value: {value!r}. Use one of: true/false, yes/no, on/off, 1/0."
    )


def _as_path(value: str) -> Path:
    """
    Convert a CLI string to a Path (no existence check).
    Use Path.exists()/is_file()/is_dir() downstream if you want strict validation.
    """
    return Path(value).expanduser()


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def acta_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `foo` and return a plain dict[str, Any].

    This is a **cookiecutter**: copy the patterns you need (positional args, optional args,
    boolean parsing, path parsing, rich help texts) and delete the rest.

    Where to plug your things:
    - Program metadata: `prog=...`, `description=...`, `epilog=...`
    - Version: `version="foo 0.1.0"` (replace with your real versioning)
    - Validation: after parsing, add checks like:
        - if args.input_path.exists() is False: parser.error(...)
        - if args.input_path.is_dir() is False: parser.error(...)

    Parameters
    ----------
    argv:
        Sequence of argument strings, typically `sys.argv[1:]`.
        If None, argparse uses `sys.argv[1:]` automatically.

    Returns
    -------
    dict[str, Any]
        A dict with parsed values. Keys match the argument `dest` names.
    """
    return None
    parser = argparse.ArgumentParser(
        prog=ACTA,
        description=(
            "foo — a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            "Examples:\n"
            "  foo 3 0.25 true 'hello' ./data\n"
            "  foo 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            "  foo 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Version flag (plug your version string here) ---
    parser.add_argument(
        "--version",
        action="version",
        version=f"{ACTA} {__version__}",
        help="Show program version and exit.",
    )

    # --- Mandatory positional arguments ---
    parser.add_argument(
        "input_int",
        type=int,
        metavar="INPUT_INT",
        help="Required integer input (e.g., 3).",
    )
    parser.add_argument(
        "input_float",
        type=float,
        metavar="INPUT_FLOAT",
        help="Required floating-point input (e.g., 0.25).",
    )
    parser.add_argument(
        "input_bool",
        type=_parse_bool,
        metavar="INPUT_BOOL",
        help="Required boolean input: true/false, yes/no, on/off, 1/0.",
    )
    parser.add_argument(
        "input_str",
        type=str,
        metavar="INPUT_STR",
        help="Required string input (quote it if it contains spaces).",
    )
    parser.add_argument(
        "input_path",
        type=_as_path,
        metavar="INPUT_PATH",
        help="Required path to a file or directory (existence not enforced by default).",
    )

    # --- Optional flags (short + long forms) ---
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Example flag (no value). Useful as a template for feature toggles.",
    )

    parser.add_argument(
        "--the-int",
        dest="the_int",
        type=int,
        default=None,
        metavar="N",
        help="Optional integer override (e.g., --the-int 7).",
    )
    parser.add_argument(
        "--the-float",
        dest="the_float",
        type=float,
        default=None,
        metavar="X",
        help="Optional float override (e.g., --the-float 3.14).",
    )
    parser.add_argument(
        "--the-boolean",
        dest="the_boolean",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean override: true/false, yes/no, on/off, 1/0.",
    )
    parser.add_argument(
        "--the-string",
        dest="the_string",
        type=str,
        default=None,
        metavar="TEXT",
        help="Optional string override (quote it if it contains spaces).",
    )
    parser.add_argument(
        "--the-path",
        dest="the_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional path override to a file or directory (existence not enforced by default).",
    )

    ns = parser.parse_args(argv)
    return vars(ns)


def milou_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `foo` and return a plain dict[str, Any].

    This is a **cookiecutter**: copy the patterns you need (positional args, optional args,
    boolean parsing, path parsing, rich help texts) and delete the rest.

    Where to plug your things:
    - Program metadata: `prog=...`, `description=...`, `epilog=...`
    - Version: `version="foo 0.1.0"` (replace with your real versioning)
    - Validation: after parsing, add checks like:
        - if args.input_path.exists() is False: parser.error(...)
        - if args.input_path.is_dir() is False: parser.error(...)

    Parameters
    ----------
    argv:
        Sequence of argument strings, typically `sys.argv[1:]`.
        If None, argparse uses `sys.argv[1:]` automatically.

    Returns
    -------
    dict[str, Any]
        A dict with parsed values. Keys match the argument `dest` names.
    """
    parser = argparse.ArgumentParser(
        prog=MILOU,
        description=(
            "foo — a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            "Examples:\n"
            "  foo 3 0.25 true 'hello' ./data\n"
            "  foo 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            "  foo 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Version flag (plug your version string here) ---
    parser.add_argument(
        "--version",
        action="version",
        version=f"{MILOU} {__version__}",
        help="Show program version and exit.",
    )

    # --- Mandatory positional arguments ---
    parser.add_argument(
        "input_int",
        type=int,
        metavar="INPUT_INT",
        help="Required integer input (e.g., 3).",
    )
    parser.add_argument(
        "input_float",
        type=float,
        metavar="INPUT_FLOAT",
        help="Required floating-point input (e.g., 0.25).",
    )
    parser.add_argument(
        "input_bool",
        type=_parse_bool,
        metavar="INPUT_BOOL",
        help="Required boolean input: true/false, yes/no, on/off, 1/0.",
    )
    parser.add_argument(
        "input_str",
        type=str,
        metavar="INPUT_STR",
        help="Required string input (quote it if it contains spaces).",
    )
    parser.add_argument(
        "input_path",
        type=_as_path,
        metavar="INPUT_PATH",
        help="Required path to a file or directory (existence not enforced by default).",
    )

    # --- Optional flags (short + long forms) ---
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Example flag (no value). Useful as a template for feature toggles.",
    )

    parser.add_argument(
        "--the-int",
        dest="the_int",
        type=int,
        default=None,
        metavar="N",
        help="Optional integer override (e.g., --the-int 7).",
    )
    parser.add_argument(
        "--the-float",
        dest="the_float",
        type=float,
        default=None,
        metavar="X",
        help="Optional float override (e.g., --the-float 3.14).",
    )
    parser.add_argument(
        "--the-boolean",
        dest="the_boolean",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean override: true/false, yes/no, on/off, 1/0.",
    )
    parser.add_argument(
        "--the-string",
        dest="the_string",
        type=str,
        default=None,
        metavar="TEXT",
        help="Optional string override (quote it if it contains spaces).",
    )
    parser.add_argument(
        "--the-path",
        dest="the_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional path override to a file or directory (existence not enforced by default).",
    )

    ns = parser.parse_args(argv)
    return vars(ns)


def quicas_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `foo` and return a plain dict[str, Any].

    This is a **cookiecutter**: copy the patterns you need (positional args, optional args,
    boolean parsing, path parsing, rich help texts) and delete the rest.

    Where to plug your things:
    - Program metadata: `prog=...`, `description=...`, `epilog=...`
    - Version: `version="foo 0.1.0"` (replace with your real versioning)
    - Validation: after parsing, add checks like:
        - if args.input_path.exists() is False: parser.error(...)
        - if args.input_path.is_dir() is False: parser.error(...)

    Parameters
    ----------
    argv:
        Sequence of argument strings, typically `sys.argv[1:]`.
        If None, argparse uses `sys.argv[1:]` automatically.

    Returns
    -------
    dict[str, Any]
        A dict with parsed values. Keys match the argument `dest` names.
    """
    parser = argparse.ArgumentParser(
        prog=QUINCAS,
        description=(
            "foo — a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            "Examples:\n"
            "  foo 3 0.25 true 'hello' ./data\n"
            "  foo 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            "  foo 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Version flag (plug your version string here) ---
    parser.add_argument(
        "--version",
        action="version",
        version=f"{MILOU} {__version__}",
        help="Show program version and exit.",
    )

    # --- Mandatory positional arguments ---
    parser.add_argument(
        "input_int",
        type=int,
        metavar="INPUT_INT",
        help="Required integer input (e.g., 3).",
    )
    parser.add_argument(
        "input_float",
        type=float,
        metavar="INPUT_FLOAT",
        help="Required floating-point input (e.g., 0.25).",
    )
    parser.add_argument(
        "input_bool",
        type=_parse_bool,
        metavar="INPUT_BOOL",
        help="Required boolean input: true/false, yes/no, on/off, 1/0.",
    )
    parser.add_argument(
        "input_str",
        type=str,
        metavar="INPUT_STR",
        help="Required string input (quote it if it contains spaces).",
    )
    parser.add_argument(
        "input_path",
        type=_as_path,
        metavar="INPUT_PATH",
        help="Required path to a file or directory (existence not enforced by default).",
    )

    # --- Optional flags (short + long forms) ---
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Example flag (no value). Useful as a template for feature toggles.",
    )

    parser.add_argument(
        "--the-int",
        dest="the_int",
        type=int,
        default=None,
        metavar="N",
        help="Optional integer override (e.g., --the-int 7).",
    )
    parser.add_argument(
        "--the-float",
        dest="the_float",
        type=float,
        default=None,
        metavar="X",
        help="Optional float override (e.g., --the-float 3.14).",
    )
    parser.add_argument(
        "--the-boolean",
        dest="the_boolean",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean override: true/false, yes/no, on/off, 1/0.",
    )
    parser.add_argument(
        "--the-string",
        dest="the_string",
        type=str,
        default=None,
        metavar="TEXT",
        help="Optional string override (quote it if it contains spaces).",
    )
    parser.add_argument(
        "--the-path",
        dest="the_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional path override to a file or directory (existence not enforced by default).",
    )

    ns = parser.parse_args(argv)
    return vars(ns)


def main(argv: Sequence[str] | None = None) -> None:
    """
    Parse CLI arguments for the multi-program `uqbar`.

    Parameters
    ----------
    argv:
        Sequence of argument strings, typically `sys.argv[1:]`.
        If None, argparse uses `sys.argv[1:]` automatically.
    """

    if argv[0] == ACTA:
        acta_core(args=acta_parser(argv))

    elif argv[0] == MILOU:
        milou_core(args=milou_parser(argv))

    elif argv[0] == QUINCAS:
        milou_core(args=milou_parser(argv))


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "main",
]
