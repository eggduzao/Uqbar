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
import sys
from typing import Any, Sequence


from uqbar._version import version


# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
__version__: str = version()


UQBAR: str = "uqbar" # Main container name | Homes all tools

ACTA: str = "acta"  # Program to generate youtube videos automatically

MILOU: str = "milou"  # Program to mass download youtube vides seamlessly

QUINCAS: str = "quincas"  # Program to produce music effortlesly without DAWs

FAUST: str = "faust"  # Program to search for strings in dirs, files and inside

DEFAULT: str = "default"  # Program to search for strings in dirs, files and inside


TRUE_VALUE_SET: list[str] = {"true", "t", "yes", "y", "1", "on"}

FALSE_VALUE_SET: set[str] = {"false", "f", "no", "n", "0", "off"}

MISSING_VALUE_SET: set[str] = {"none", "null", "nul", "nan", "na", "n/a", "void"}


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
    if v in TRUE_VALUE_SET:
        return True
    if v in FALSE_VALUE_SET:
        return False
    if v in MISSING_VALUE_SET:
        return None
    raise argparse.ArgumentTypeError(
        f"Invalid boolean value: {value!r}. Use one of: \n"
        f"  - True Values: {", ".join(sorted(TRUE_VALUE_SET))}\n"
        f"  - False Values: {", ".join(sorted(FALSE_VALUE_SET))}\n"
        f"  - NA Values: {", ".join(sorted(MISSING_VALUE_SET))}\n"
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
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog=ACTA,
        description=(
            f"{ACTA} - a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {ACTA} 3 0.25 true 'hello' ./data\n"
            f"  $ {UQBAR} {ACTA} 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            f"  $ {UQBAR} {ACTA} 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"{ACTA} {__version__}",
        help="Show program version and exit.",
    )

    # Positional arguments
    ###

    # Optional arguments
    ###

    ns = parser.parse_args(argv)
    return vars(ns)


def milou_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `foo` and return a plain dict[str, Any].

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
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog=MILOU,
        description=(
            f"{MILOU} - a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {MILOU} 3 0.25 true 'hello' ./data\n"
            f"  $ {UQBAR} {MILOU} 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            f"  $ {UQBAR} {MILOU} 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"{MILOU} {__version__}",
        help="Show program version and exit.",
    )

    # Positional arguments
    parser.add_argument(
        "input_int",
        type=int,
        metavar="INPUT_INT",
        help="Required integer input (e.g., 3).",
    )

    # Optional arguments
    parser.add_argument(
        "--the-boolean",
        dest="the_boolean",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean override: true/false, yes/no, on/off, 1/0.",
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
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog=QUINCAS,
        description=(
            f"{QUINCAS} - a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {QUINCAS} 3 0.25 true 'hello' ./data\n"
            f"  $ {UQBAR} {QUINCAS} 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            f"  $ {UQBAR} {QUINCAS} 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"{QUINCAS} {__version__}",
        help="Show program version and exit.",
    )

    # Positional arguments
    parser.add_argument(
        "input_int",
        type=int,
        metavar="INPUT_INT",
        help="Required integer input (e.g., 3).",
    )

    # Optional arguments
    parser.add_argument(
        "--the-boolean",
        dest="the_boolean",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean override: true/false, yes/no, on/off, 1/0.",
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


def faust_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `faust` and return a plain dict[str, Any].

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
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog=FAUST,
        description=(
            f"{FAUST} - a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {FAUST} -l . -s '*.png'\n"
            f"  $ {UQBAR} {FAUST} --location=/ --recursive --type file --string 'cat' \\\n"
            f"      --output absdir filename --colour\n"
            f"  $ {UQBAR} {FAUST} -l / -r -t dir file content metadata -s 'cat photos' \\\n"
            f"      -o reldir filename fileline trim250 -c\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"{FAUST} {__version__}",
        help="Show program version and exit.",
    )

    parser.add_argument(
        "-l",
        "--location",
        nargs="*",
        default=None,
        help="One or more directories/files to search (default: current directory only).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search recursively within the locations.",
    )
    parser.add_argument(
        "-t",
        "--type",
        nargs="*",
        default=None,
        help="One or more of: dir file content metadata (wildcards allowed). Default: content",
    )
    parser.add_argument(
        "-s",
        "--string",
        nargs="+",
        required=True,
        help="One or more search queries (wildcards or regex via /.../ or r:...).",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="*",
        default=None,
        help="Output columns. Default: reldir filename fileline trim50",
    )
    parser.add_argument(
        "-c",
        "--colour",
        action="store_true",
        help="Enable ANSI colours and bold matches (best-effort).",
    )

    ns = parser.parse_args(argv)
    return vars(ns)


def default_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `default` and return a plain dict[str, Any].

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
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog=DEFAULT,
        description=(
            f"{DEFAULT} - a reference CLI demonstrating clean argparse patterns.\n\n"
            "It includes mandatory positional inputs (int/float/bool/str/path) and optional\n"
            "flags with both short and long forms. Copy/paste and tailor as needed."
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {DEFAULT} 3 0.25 true 'hello' ./data\n"
            f"  $ {UQBAR} {DEFAULT} 3 0.25 false 'hello' ./data --the-int 7 --the-path ~/Downloads\n"
            f"  $ {UQBAR} {DEFAULT} 3 0.25 yes 'hello' ./data -e --the-boolean off\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"{DEFAULT} {__version__}",
        help="Show program version and exit.",
    )

    # Positional arguments
    parser.add_argument(
        "input_int",
        type=int,
        metavar="INPUT_INT",
        help="Required integer input (e.g., 3).",
    )

    # Optional arguments
    parser.add_argument(
        "--the-boolean",
        dest="the_boolean",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean override: true/false, yes/no, on/off, 1/0.",
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


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse CLI arguments for the multi-program `uqbar`.

    Parameters
    ----------
    argv:
        Sequence of argument strings, typically `sys.argv[1:]`.
        If None, argparse uses `sys.argv[1:]` automatically.
    """
    return_status: int = 1

    if argv[0] == ACTA:
        return_code: int = 2
        from uqbar.acta.core import acta_core
        return_status = acta_core(args=acta_parser(argv[1:]))

    elif argv[0] == MILOU:
        return_code: int = 2
        from uqbar.milou.core import milou_core
        return_status = milou_core(args=milou_parser(argv[1:]))

    elif argv[0] == QUINCAS:
        return_code: int = 2
        from uqbar.quincas.core import quincas_core
        return_status = quicas_core(args=quicas_parser(argv[1:]))

    elif argv[0] == FAUST:
        return_code: int = 2
        from uqbar.faust.core import faust_core
        return_status = faust_core(args=faust_parser(argv[1:]))

    elif argv[0] == DEFAULT:
        return_code: int = 2
        from uqbar.default.core import default_core
        return_status = default_core(args=default_parser(argv[1:]))

    if return_status == 1:

        raise_message: str = (
            f"Available tools in version {__version__} are:"
            f"{ACTA}, {MILOU}, {QUINCAS}, {FAUST}, {DEFAULT}"
            f"Please select one of the available tools and use -h"
            f"if you need further help."
        )
    return return_status


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "main",
]
