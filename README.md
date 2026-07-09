# Chord Transposer

Web app for transposing `.docx` chord sheets between musical keys. Preserves document formatting and supports both standard and German (H-notation) chord notation.

## Usage

### Web app

```bash
pip install -r requirements-dev.txt
flask run
```

Open `http://localhost:5000`, upload a `.docx` chord sheet, select the current and target key, and download the transposed file.

### CLI

```bash
python transpose.py
```

Processes all `.docx` files in `input/` and saves results to `output/`.

### Docker

```bash
docker compose up
```

## Development

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest
```

Coverage of `transpose.py` must stay at or above 95%.

## License

Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See [LICENSE](LICENSE) for the full text.

Copyright (C) 2026 Aierizer Dániel
