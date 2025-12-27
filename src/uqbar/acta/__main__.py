# SPDX-License-Identifier: MIT
# uqbar/acta/__main__.py
"""
Acta Diurna | Main
==================

Overview
--------
Entry point for `python -m uqbar.acta` and the console script.

Parameters
----------
argv :
    Optional sequence of CLI arguments. If None, `sys.argv[1:]` is used
    (handled implicitly by `argparse`).

Metadata
--------
- Project: Acta diurna
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import sys


from uqbar.cli import acta_parser
from uqbar.acta.core import acta_core


# -------------------------------------------------------------------------------------
# Entry Point | python -m uqbar.acta > out.txt 2&<1
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    raise SystemExit(acta_core(acta_parser(sys.argv[1:])))
