# Chord Transposer — Agent Rules

Small Flask app that transposes `.docx` chord sheets between musical keys.
Core logic lives in `src/transpose.py`; the web layer is `src/app.py` with a
single Tailwind (CDN) template at `src/templates/index.html`.

## Mandatory: run all Python checks after any change

After ANY change to Python code, tests, or config, run the full check suite
before considering the task done. Use the `/check` command, or run directly:

```bash
ruff check .
ruff format --check .
pytest
```

- `pytest` is configured (in `pyproject.toml`) to run with coverage and to
  fail if combined coverage of `transpose.py` and `app.py` drops below 95%.
- `testpaths` includes three test files: `src/test_transpose.py`,
  `src/test_app.py`, and `src/test_integration.py`. All three must pass. Do
  not remove any from `testpaths`.
- `src/test_integration.py` contains end-to-end integration tests using real
  `.docx` bytes. When adding new behaviour to `src/transpose.py` or
  `src/app.py`, consider whether a corresponding integration test is needed
  there.
- Fix all lint, formatting, test, and coverage failures. Never leave the suite red.
- If a change lowers coverage, add or update tests to restore it.

## Conventions

- Do not add explanatory code comments; use self-explanatory names instead.
- Install dev tooling with `pip install -r requirements-dev.txt`.
