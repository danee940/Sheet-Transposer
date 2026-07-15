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
python src/transpose.py
```

Processes all `.docx` files in `input/` and saves results to `output/`.

### Docker

```bash
docker compose up
```

Runs the app on `http://localhost:5000` alongside a Gotenberg service for PDF conversion.

## Development

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest
```

Coverage of `transpose.py` must stay at or above 95%.

## Support

If you find this project useful, you can support its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/danee940)

## License

Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See [LICENSE](LICENSE) for the full text.

Copyright (C) 2026 Aierizer Dániel
