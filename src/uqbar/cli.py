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
import datetime as dt
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

from uqbar._version import version

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
__version__: str = version()

CURRENT_WORKING_DIR: Path = Path.cwd()


# Main container
UQBAR: str = "uqbar" # Main container name | Homes all tools

# Automation for social media
ACTA: str = "acta"  # Program to generate youtube videos automatically

# Fetch/Send through Network/Web
MILOU: str = "milou"  # Program to mass download youtube vidos, book pdfs, etc

# Music programming
QUINCAS: str = "quincas"  # Program to produce music effortlesly without DAWs

# Search of any nature
FAUST: str = "faust"  # Program to search for strings in dirs, files and inside

# Prompt generator
TIETA: str = "tieta"  # Program to generate claude prompts for summary-expansion

# Datetime/Calendar-related tasks
LOLA: str = "lola" # Program to perform datetime-related tasks

# Cookiecutter
DEFAULT: str = "default"  # Program to search for strings in dirs, files and inside


TRUE_VALUE_SET: set[str] = {"true", "t", "yes", "y", "1", "on"}

FALSE_VALUE_SET: set[str] = {"false", "f", "no", "n", "0", "off"}

MISSING_VALUE_SET: set[str] = {"none", "null", "nul", "nan", "na", "n/a", "void"}


SPLIT_PATTERN = r"[ ,;|\t\n]+"

# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _parse_bool(value: str) -> bool | None:
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


def _as_path_list(value: str) -> list[Path]:
    """
    Convert a CLI string to a list of Path (no existence check).
    Use Path.exists()/is_file()/is_dir() downstream if you want strict validation.
    """

    # Use re.split() to perform the split
    value_list = re.split(SPLIT_PATTERN, value)
    return [Path(e).expanduser() for e in value_list]


def _as_datetime(value: str) -> str | None:
    """
    Validate and normalize a date string.

    Accepts the following input formats:
        - ``DD.MM.YYYY``
        - ``DD/MM/YYYY``
        - ``YYYY-MM-DD``

    If valid, returns the date normalized to ISO format ``YYYY-MM-DD``.
    If invalid, prints a user-facing message and returns ``None``.

    Parameters
    ----------
    value : str
        Date string to be validated and normalized.

    Returns
    -------
    str | None
        Normalized date string in ``YYYY-MM-DD`` format if valid,
        otherwise ``None``.

    Notes
    -----
    - No exceptions are raised.
    - Parsing is strict (invalid calendar dates are rejected).
    """

    _FORMATS: Final[tuple[str, ...]] = (
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
    )

    for fmt in _FORMATS:
        try:
            parsed = dt.datetime.strptime(value, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    print(
        "Invalid date format. Please use one of the following: "
        "DD.MM.YYYY, DD/MM/YYYY, or YYYY-MM-DD."
    )
    return None

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
            f"  $ {UQBAR} {ACTA} --help\n"
            f"  $ {UQBAR} {ACTA} ./root/\n"
            f"  $ {UQBAR} {ACTA} ./root/ -d 2026-07-31 --s '1,2,5,6,7,8,9'\n"
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
    parser.add_argument(
        "root_path",
        type=_as_path,
        metavar="PATH",
        help="Main path to store all data.",
    )

    # Optional arguments
    parser.add_argument(
        "-d",
        "--date",
        dest="this_date",
        type=_as_datetime,
        default=None,
        metavar="DATE",
        help="Date in which to fetch trends. Keep empty for latest trends.",
    )
    parser.add_argument(
        "-s",
        "--semaphore",
        dest="semaphore",
        type=str,
        default=None,
        metavar="INPUT_STR",
        help="Which steps of the pipeline to run as a comma-separated list of int",
    )

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
            f"{MILOU} - a CLI tool to fetch artefacts from the internet: from \n"
            "youtube videos to books in various formats.\n\n"
            "Milou - known as Snowy in English - is a fictional white Wire Fox \n"
            "Terrier who is a companion to Tintin, the series' protagonist. Snowy \n"
            "made his debut on 1929, helping Tintin in variety of ways, including \n"
            "fetching missing artifacts.\n\n"
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {MILOU} book -i ~/Desktop/search_terms.txt -o ~\n"
            f"  $ {UQBAR} {MILOU} book -q 'the,adventures,of,tintim,herge' -s "
            "'google,duckduckgo' -o ~\n"
            f"  $ {UQBAR} {MILOU} book -i ~/Desktop/search_terms.txt -f 'pdf,epub,djvu' -o ~\n"
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
        "command_subtipe",
        type=str,
        metavar="SUBCOMMAND",
        help="Requested item to be fetched. Currently in ['youtube', 'book']",
    )

    # Optional arguments
    parser.add_argument(
        "-i",
        "--input-path",
        dest="input_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Input path as a text file with one query list of strings per line.",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        dest="output_path",
        type=_as_path,
        default=CURRENT_WORKING_DIR,
        metavar="PATH",
        help="Location to output the search results.",
    )
    parser.add_argument(
        "-q",
        "--query",
        dest="query",
        type=str,
        default=None,
        metavar="INPUT_STR,[INPUT_STR2,...]",
        help="Optional single comma-separated list of strings as a query.",
    )
    # Optional arguments
    parser.add_argument(
        "-s",
        "--search-engines",
        dest="search_engines",
        type=str,
        default=None,
        metavar="INPUT_STR,[INPUT_STR2,...]",
        help="Optional comma-separated list of formats allowed.",
    )
    # Optional arguments
    parser.add_argument(
        "-f",
        "--formats-allowed",
        dest="formats_allowed",
        type=str,
        default=None,
        metavar="INPUT_STR,[INPUT_STR2,...]",
        help="Optional comma-separated list of formats allowed.",
    )

    ns = parser.parse_args(argv)
    return vars(ns)


def quincas_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
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


def tieta_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `tieta` and return a plain dict[str, Any].

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
        prog=TIETA,
        description=(
            f"{TIETA} - a CLI tool to create input text prompts for Claude, based "
            "on an input `pdf` file.\n\nTieta is a character from the homonimous "
            "book by the Brazilian writer Jorge Amado. This fascinating novel "
            "revolves around a young woman, named Tieta, who lives in a small town "
            "in Brazil. Tieta is a naive girl, who is ostracised by the entire "
            "community, for her exhuberant beauty. She leaves the town to go to "
            "a big city, where she becomes rich and powerful; and when she decides "
            "to return to her home town, things are not quite the same."
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {TIETA} claude -i input.pdf -o output.txt -s 10 -f 20\n"
            f"  $ {UQBAR} {TIETA} gpt -i ./loc1/file.txt -o ./out-loc/output.txt\n"
            f"  $ {UQBAR} {TIETA} gpt -l ./loc1/,./loc2/ -o ./out-loc/output.txt\n"
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
        "command_subtipe",
        type=str,
        metavar="SUBCOMMAND",
        help="Requested prompt type. Currently in ['claude', 'gpt']",
    )

    # Optional arguments
    parser.add_argument(
        "-i"
        "--input-path",
        dest="input_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional input as a path to a pdf file.",
    )
    parser.add_argument(
        "-l"
        "--input-path-list",
        dest="input_path_list",
        type=_as_path_list,
        default=None,
        metavar="PATH[,PATH,...]",
        help="Optional input as a list of paths containing files.",
    )
    parser.add_argument(
        "-o"
        "--output-path",
        dest="output_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional name of text output file path.",
    )
    parser.add_argument(
        "-s",
        "--start-page",
        dest="start_page",
        type=int,
        default=None,
        metavar="INPUT_INT",
        help="Optional number of first page to be parsed and returned.",
    )
    # Optional arguments
    parser.add_argument(
        "-f",
        "--final-page",
        dest="final_page",
        type=int,
        default=None,
        metavar="INPUT_INT",
        help="Optional number of last page to be parsed and returned.",
    )
    # Optional arguments
    parser.add_argument(
        "-r",
        "--redflags",
        dest="redflags",
        type=_parse_bool,
        default=None,
        metavar="{true|false}",
        help="Optional boolean. Whether to print pdf parsing red flags.",
    )
    parser.add_argument(
        "-p",
        "--redflags-path",
        dest="redflags_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional path. Location where pdf parsing red flags will be written.",
    )

    ns = parser.parse_args(argv)
    return vars(ns)

def lola_parser(argv: Sequence[str] | None = None) -> dict[str, Any]:
    """
    Parse CLI arguments for the program `lola` and return a plain dict[str, Any].

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
        prog=LOLA,
        description=(
            f"{LOLA} - a CLI-based tool to perform multiple datetime-related \n"
            "tasks.\n"
            "Lola is the main character from the German movie 'Lola Rennt'. \n"
            "In this movie, it will be shown how an otherwise negligible \n"
            "difference in a few seconds can change the life of everyone. \n"
            "Including Lola, who must run exhaustively to save her partner.\n\n"
        ),
        epilog=(
            f"Examples:\n"
            f"  $ {UQBAR} {LOLA} todo\n"
            f"  $ {UQBAR} {LOLA} todo -e 2048-10-31 -o ~/todo.txt\n"
            f"  $ {UQBAR} {LOLA} todo --date-start 2048-02-01 --date-end 2048-10-31\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"{LOLA} {__version__}",
        help="Show program version and exit.",
    )

    # Positional arguments
    parser.add_argument(
        "command_subtipe",
        type=str,
        metavar="SUBCOMMAND",
        help="Requested item to be fetched. Currently in ['todo']",
    )

    # Optional arguments
    parser.add_argument(
        "-s",
        "--date-start",
        dest="date_start",
        type=_as_datetime,
        default=None,
        metavar="DATETIME",
        help="Optional start date of .todo file creation (default: start of year).",
    )
    parser.add_argument(
        "-e",
        "--date-end",
        dest="date_end",
        type=_as_datetime,
        default=None,
        metavar="DATETIME",
        help="Optional end date of .todo file creation (default: end of year).",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        dest="output_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional path. Location where the .todo file will be written.",
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


def main(argv: Sequence[str] | None) -> int:
    """
    Parse CLI arguments for the multi-program `uqbar`.

    Parameters
    ----------
    argv:
        Sequence of argument strings, typically `sys.argv[1:]`.
        If None, argparse uses `sys.argv[1:]` automatically.
    """
    return_status: int = 1

    if not argv:
        return return_status

    if argv[0] == ACTA:
        from uqbar.acta.core import acta_core
        return_status = acta_core(args=acta_parser(argv[1:]))

    elif argv[0] == MILOU:
        from uqbar.milou.core import milou_core
        return_status = milou_core(args=milou_parser(argv[1:]))

    elif argv[0] == QUINCAS:
        from uqbar.quincas.core import quincas_core
        return_status = quincas_core(args=quincas_parser(argv[1:]))

    elif argv[0] == FAUST:
        from uqbar.faust.core import faust_core
        return_status = faust_core(args=faust_parser(argv[1:]))

    elif argv[0] == TIETA:
        from uqbar.tieta.core import tieta_core
        return_status = tieta_core(args=tieta_parser(argv[1:]))

    elif argv[0] == LOLA:
        from uqbar.lola.core import lola_core
        return_status = lola_core(args=lola_parser(argv[1:]))

    # elif argv[0] == DEFAULT:
    #     from uqbar.default.core import default_core
    #     return_status = default_core(args=default_parser(argv[1:]))

    return return_status


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "main",
]
