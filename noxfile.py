import nox

PACKAGE = "magnetohydrodynamics"


@nox.session(python=["3.10", "3.11", "3.12"])
def tests(session):
    """Run the test suite with pytest."""
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run("pytest", "--cov", PACKAGE, "--cov-report=term-missing")


@nox.session
def lint(session):
    """Run static code quality tools."""
    session.install("ruff")
    session.run("ruff", "check", PACKAGE, "tests")


@nox.session
def format(session):
    """Automatically format source code."""
    session.install("black")
    session.run("black", PACKAGE, "tests")


@nox.session
def typecheck(session):
    """Run MyPy static type checking."""
    session.install("mypy")
    session.install("-e", ".")
    session.run("mypy", PACKAGE)


@nox.session
def docs(session):
    """Build documentation with Sphinx."""
    session.install("-e", ".[docs]")
    session.run("sphinx-build", "docs", "docs/_build")
