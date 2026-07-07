# Sheet Transposer — Agent Rules

Small Flask app that transposes `.docx` chord sheets between musical keys.
Core logic lives in `transpose.py`; the web layer is `app.py` with a single
Tailwind (CDN) template at `templates/index.html`.

## Mandatory: run all Python checks after any change

After ANY change to Python code, tests, or config, run the full check suite
before considering the task done. Use the `/check` command, or run directly:

```bash
ruff check .
ruff format --check .
pytest
```

- `pytest` is configured (in `pyproject.toml`) to run with coverage and to
  fail if coverage of `transpose.py` drops below 95%.
- Fix all lint, formatting, test, and coverage failures. Never leave the suite red.
- If a change lowers coverage, add or update tests to restore it.

## Conventions

- Do not add explanatory code comments; use self-explanatory names instead.
- Keep the app dependency-light and pure-Python (no Node build pipeline).
- Install dev tooling with `pip install -r requirements-dev.txt`.
