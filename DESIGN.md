# **Magnetohydrodynamics – Design Document**

> High-level design and architecture notes for the `magnetohydrodynamics` Python package.

---

## **1. Overview**

`magnetohydrodynamics` is a modern Python library for <brief one-line purpose; e.g. _“simulating and analyzing magnetohydrodynamic systems with a clean, testable API”_>.

This document captures the **high-level architecture**, **design choices**, and **extension points** of the project.  
It is meant for:

- Contributors who want to understand how the system is structured.
- Reviewers and maintainers making medium/long-term design decisions.
- Future you, trying to remember why we did things *this* way.

---

## **2. Goals and Non-Goals**

### 2.1. Goals

- ✅ Provide a **clear, documented public API** for end users (`magnetohydrodynamics.*`).
- ✅ Separate **core domain logic** from I/O, CLIs, and infrastructure concerns.
- ✅ Be **easy to test**: components are small, composable, and deterministic where possible.
- ✅ Support **type checking** (mypy/pyright) and **static analysis** (ruff/flake8/pylint).
- ✅ Allow future **performance-critical extensions** in C/C++/Rust via extension modules.

### 2.2. Non-Goals

- ❌ Not a full-featured GUI application.
- ❌ Not a monolithic research notebook; notebooks live in `notebooks/` as examples,
  not as the primary API.
- ❌ Not a “kitchen sink” framework with every feature; the scope is deliberately focused.

---

## **3. High-Level Architecture**

At the top level:

- `src/magnetohydrodynamics/`
  - **Public API modules**: what users import.
  - **Internal modules**: implementation details (`_internal` or `_core` namespaces).
- `tests/`
  - Unit, integration, and regression tests.
- `docs/`
  - User-facing and developer-facing documentation.
- `examples/` and `notebooks/`
  - Usage examples, tutorials, and reference workflows.

A common mental model:

```text
[CLI / UI] --> [Public API layer] --> [Domain / Core] --> [Numerical / Extension Modules]
                      |                       |
                  [Adapters]             [I/O, serialization]
```

---

## **4. Module Layout (Proposed)**

Adjust names to your real package later; this is a reusable template.

Inside src/magnetohydrodynamics/:
- __init__.py
- Defines the public API surface (__all__, user-facing imports).
- __about__.py
- Centralized metadata (version, author, license).
- _version.py
- Version management (e.g. via importlib.metadata or versioneer).
- __main__.py
- Entry point for python -m magnetohydrodynamics (CLI wrapper).

Suggested submodules:
- `core/`
  - Pure domain logic; no I/O, no CLI.
  - E.g. equations.py, solvers.py, grid.py, state.py.
- `io/`
  - Reading and writing domain objects to disk (HDF5, NetCDF, JSON, etc.).
- `cli/`
  - Click/typer/argparse entry points that call into the public API.
- `visualization/`
  - Plotting helpers (matplotlib/plotly), always optional dependencies.
- `ext/`
  - Optional compiled extensions (C/C++/Rust via pybind11/cffi/etc.).
- `utils/` (or `_utils/`)
  - Internal helpers (logging, configuration, common math helpers).

---

## **5. Data Flow**

1. **Input Layer**
  - **User calls:** ....
  - **Python API:** `magnetohydrodynamics.solver.solve(...)`, or
  - **CLI:** magnetohydrodynamics run ....
  - **Configuration can come from:**
    - Function arguments,
    - dataclass/Pydantic models,
    - or config files (`YAML`/`TOML`) parsed in `cli/io`.
2. **Domain Layer**
  - "Core" modules build domain objects (states, fields, equations).
  - Numerical routines operate on them (finite difference, spectral, etc.).
  - Business rules / physics priors live here.
3. **Output Layer**
  - **Results are:**
    - Returned to the caller as Python objects,
    - Serialized to disk (`io`),
    - Or visualized (`visualization`).

---

## **6. Error Handling & Logging**

- **Use Python exceptions for error signaling:**
  - Define custom exceptions in exceptions.py (e.g. ConfigurationError, SolverError).
- **Use the standard logging library:**
  - A single logger namespace: logger = logging.getLogger("magnetohydrodynamics").
  - No printing inside core modules (only logging).

---

## **7. Configuration Strategy**

- Prefer explicit parameters in public APIs.
- For more complex workflows, use:
  - Data classes or Pydantic models for structured config.
  - Optional config files (.yaml / .toml), parsed in CLI layer only.
- Keep defaults safe and conservative (e.g. stable numerical schemes, modest resolution).

---

## **8. Performance and Extensions**

- Start with pure Python + NumPy where possible.
- If/when profiling reveals bottlenecks:
  - Move hot spots into ext/ via pybind11, Cython, or numba.
- Maintain a clear boundary:
  - Pure Python orchestrates control flow.
  - Lower-level modules handle tight loops and numeric kernels.

---

## **9. Testing Strategy**

- **`tests/`**:
  - test_core_*.py - unit tests for core domain logic.
  - test_integration_*.py - multi-component flows.
  - test_cli_*.py - CLI behavior (arg parsing, exit codes).
- **Use pytest with**:
  - Fixtures for shared setups,
  - Parametrization for numerical cases,
  - Optional slow/large tests marked with @pytest.mark.slow.

---

## **10. Documentation**

- **`docs/`**: built with Sphinx or MkDocs.
- **Structure**:
  - User Guide - installation, quickstart, tutorials.
  - API Reference - auto-generated from docstrings.
  - Developer Guide - contribution guidelines, architecture (this document).
  - Enforce docstring style (e.g. NumPy or Google style) via linters and CI.

---

## **11. Extensibility and Roadmap**

- Keep the public API minimal but expressive so it can grow later.
- Plan for:
  - New solvers or numerical schemes.
  - Additional backends / hardware (e.g. GPU support).
  - Integration with larger ecosystems (e.g. Dask, JAX, or domain-specific tools).

---

## **12. Open Questions / TODOs**

- [x] Finalize which submodules are public vs. internal (_internal, _ext).
- [ ] Decide on the long-term config pattern (simple kwargs vs. config objects).
- [ ] Define explicit stability guarantees for the public API (semantic versioning).
- [ ] Add diagrams (class diagrams, data flow) to this document and docs/.

---

Last updated: 2025-12-05
Maintainers: Eduardo G Gusmao

---
