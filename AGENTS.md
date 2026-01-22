# Agent Guidelines for Stay-On-Track

## Commands
- **Install**: `poetry install`
- **Lint**: `poetry run ruff check . --fix && poetry run black . && poetry run isort .`
- **Test all**: `poetry run pytest`
- **Test single**: `poetry run pytest tests/test_file.py::test_function -v`
- **Type check**: `poetry run mypy src`
- **Build**: `poetry run pyinstaller build.spec`

## Code Style
- **Line length**: 100 (Black/Ruff enforced)
- **Python**: 3.8+ syntax, target 3.8-3.12
- **Imports**: stdlib, third-party, local (isort profile=black)
- **Naming**: `PascalCase` classes, `snake_case` functions/vars, `_private` prefix, `UPPER_CASE` constants
- **Types**: Optional; mypy is permissive (`disallow_untyped_defs = false`)
- **Strings**: f-strings preferred
- **Files**: Use `with open(..., encoding="utf-8")`
- **Errors**: Specific exceptions, fallback to defaults, print for logging
- **Docstrings**: Triple-quoted, brief one-liners acceptable

## Pre-commit
Runs Black, isort, Ruff on commit. Install: `poetry run pre-commit install`
