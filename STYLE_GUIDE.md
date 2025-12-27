# **Magnetohydrodynamics - Style Guide**

This document defines the coding and contribution style for the
**Magnetohydrodynamics** project. The goal is to keep the codebase
consistent, readable, and easy to review.

---

## Philosophy

This project follows Python’s **"The Zen of Python" (PEP 20)** guiding principles:

> Beautiful is better than ugly.
> Explicit is better than implicit.
> Simple is better than complex.
> Complex is better than complicated.
> Flat is better than nested.
> Sparse is better than dense.
> Readability counts. (...)
>
> — *Tim Peters*

For the full version, just type:
```python
import this
```

---

## **1. General Principles**

- Prefer **clarity over cleverness**.
- Optimize for **maintainability** rather than micro-performance.
- All new code **must be typed**, **lint-clean**, and **covered by tests**
  when it introduces new behavior.

---

## **2. Language & Version**

- Primary language: **Python 3.12+**
- **Type hints are required** for all public functions, methods, and modules.

Example:

```python
def evolve_state(state: State, dt: float) -> State:
    ...
```

---

## 3. **Code Style**

#### Code style is enforced automatically using:

- `ruff` (linting & some formatting)
- `black`-compatible formatting (via `ruff` where configured)
- `isort`-style import ordering (also via `ruff`)
- `mypy` / `pyright` for type checking

Run locally:

```bash
ruff check src tests
ruff format src tests
mypy src tests
pytest
```

Key conventions:
- Maximum line length: **88 characters** (`black` default).
- Use **spaces**, not tabs.
- **4 spaces** per indent level.
- **Avoid wildcard imports** for readability and maintainability (`from x import *`).

---

## **4. Project Layout**

- Library code: `src/magnetohydrodynamics/`
- Tests: `tests/`
- Docs: `docs/`
- Examples: `examples/`
- Notebooks (exploratory only): `notebooks/`

#### Tests should mirror the package structure:
- `src/magnetohydrodynamics/core.py` -> `tests/test_core.py`

---

## **5. Imports**

Import order (`black` default):
  1. `from __future__ import annotations`
  2. Standard libraries
  3. Third-party packages
  4. Local application imports

Example:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from magnetohydrodynamics.io import load_snapshot
from magnetohydrodynamics.solver import advance
```

---

# **6. Docstrings**

## Docstrings must be in **NumPy style** for all public functions,
classes, and modules.

Example:

```python
def integrate_field(field: np.ndarray, dt: float) -> np.ndarray:
    """
    Integrate the field forward in time by one step.

    Parameters
    ----------
    field : np.ndarray
        The current field values on the simulation grid.
    dt : float
        Time step size.

    Returns
    -------
    np.ndarray
        Updated field after one integration step.
    """
```

Internal/private helpers (`_helper`) may have shorter docstrings, but
should still explain **purpose** and **arguments**.

Module-docstrings are **highly encouraged**, follow the examples seen in
`src/magnetohydrodynamics/`.

---

## **7. Error Handling & Logging**

- Raise specific exceptions (e.g., ValueError, TypeError,
RuntimeError) with clear messages.
- Do not print from library code; use Python's logging module.
- Default log level for the library should be WARNING.

---

## **8. Testing**

- Test framework: `pytest`
- Location: `tests/`
- All new features **require tests**.
- Bug fixes must include **regression tests** that fail before the fix
and pass after.

#### Guidelines:
- Prefer **small, focused tests**.
- Use **parametrization** when testing multiple similar cases.
- **Avoid** reliance on **external network / filesystem** when possible; use
temporary directories and fixtures.

---

## **9. Configuration Files**

- Linting: `.flake8`, `ruff.toml`
- Typing: `.mypy.ini`, `pyrightconfig.json`
- Pre-commit hooks: `.pre-commit-config.yaml`

Developers should **enable pre-commit** locally:

```bash
pre-commit install
```

---

## **10. Git & Collaboration**

#### **Branch Names**

Use **descriptive**, **kebab-case** names:
- `feature/add-parallel-solver`
- `fix/bc-handling-edge-cells`
- `docs/improve-installation-guide`

#### **Commit Messages**
- Working language is English for **inclusion**; however,
in special cases you may use other language or devices. Please
check our ``CODE_OF_CONDUCT.md`` for more information.
- Use **imperative present tense**: Add, Fix, Refactor.
- Keep subject line **<= 72 chars** when possible.
- Optionally include a short body explaining **why**, not just what.

Example:

```text
Add staggered-grid MHD solver

Improves stability at high Alfvén speeds and prepares for AMR support.
```

---

## **11. Public API**

- All exported symbols **should be listed in `__all__`** where appropriate.
- The public API should be **re-exported** from `magnetohydrodynamics/__init__.py`.
- Avoid breaking changes to the public API without bumping the MAJOR
version and documenting in `CHANGELOG.md`.

---

## **12. Performance**

- Write **clear code first**; optimize hotspots only after measuring.
- For tight loops, consider:
  - `NumPy` vectorization
  - `C`/`C++`/`Cython`/`numba` extensions (behind a **clean** Python interface)

Any performance-critical paths **must remain well-tested**.

---

## **13. Documentation**

- **User-facing documentation** lives in `docs/` and is built with `Sphinx`.
- Every new feature that changes behavior **must be reflected in the `docs`**.
- Keep `README.md` focused on **what it is**, **how to install**, and
**quickstart**. I.e. Avoid verbosity.

---

## **14. Section Rulers**

To separate sections, classes, functions and have a uniform ASCII-safe separator,
we propose the following scheme:

#### Double-hash header
- Use the double-hash header at the start of new sections on the code.
- Standardize to exactly 88 characters.

Example:
```python
## -------------------------------------------------------------------------------------
## Class Funcions
## -------------------------------------------------------------------------------------
```

#### Single-hash header
- Use the single-hash header at the start of new section's items on the code.
- Use them to separate important sections of a single long class.
- Standardize to exactly 88 characters.

Example:
```python
# --------------------------------------------------------------------------------------
# Class decorator functions
# --------------------------------------------------------------------------------------
```

#### Block comment banner
- Use the block comment banner to pinpoint certain locations of the code that are not trivial.
- Standardize to exactly 88 characters.

Example:
```python
# ==================================== Special Case ====================================
```

#### Docstring-style banner
- Use the docstring-style banner only at error/warning-prone locations you might want to pinpoint.
- Also, use them to pinpoint legacy comments or code and to warn user about low-performance (and others).
- Standardize to exactly 88 characters.

Example:
```python
# ======================================================================================
# Use only if necessary | Time-consuming loop
# ======================================================================================
```

**When in doubt:** Always use the 'Single-hash header'.

---

By contributing to **Magnetohydrodynamics**, you agree to follow this
style guide so the project remains pleasant to work on for **everyone**.
