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

## Deploy to Railway

The app needs a companion Gotenberg service for PDF output, so a Railway project
runs two services:

1. Create a Railway project and add this repository. Railway builds the app from
   the `Dockerfile` (see `railway.json`) and injects `PORT`.
2. Add a second service from the Docker image `gotenberg/gotenberg:8`.
3. On the app service, set `GOTENBERG_URL` to the Gotenberg service's private
   address, e.g. `http://gotenberg.railway.internal:3000`.
4. Generate a public domain for the app service. Railway terminates HTTPS.

The `/health` endpoint is used as the deploy healthcheck.

## Styling

The stylesheet is prebuilt with Tailwind into `src/static/tailwind.css` and shipped
as a normal static asset, so no CDN runs in the browser. The committed CSS file is
cache-busted via a content hash appended as `?v=` to its URL, and served with a
long-lived immutable cache header, while HTML pages are sent with `no-cache`.

Rebuild the stylesheet after changing markup or `tailwind.config.js`:

```bash
npm install
npm run build:css
```

Use `npm run watch:css` during development. Commit the regenerated
`src/static/tailwind.css`; the Docker image does not build it.

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
