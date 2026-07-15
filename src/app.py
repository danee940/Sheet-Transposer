"""Flask web frontend for transposing chord sheets in .docx format."""

import hashlib
import json
import logging
import os
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from zipfile import BadZipFile

from docx.opc.exceptions import PackageNotFoundError
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, send_file

import seo
from seo import FAQ_ITEMS, HOWTO_STEPS, SITE_URL
from transpose import (
    InvalidKeyError,
    PdfConversionError,
    convert_docx_to_pdf,
    transpose_document_bytes,
)

load_dotenv()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_SEMITONES = 11

DOCX_MIMETYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIMETYPE = "application/pdf"

KEY_OPTIONS = [
    "C",
    "C#",
    "Db",
    "D",
    "D#",
    "Eb",
    "E",
    "F",
    "F#",
    "Gb",
    "G",
    "G#",
    "Ab",
    "A",
    "A#",
    "Bb",
    "B",
    "Cm",
    "C#m",
    "Dbm",
    "Dm",
    "D#m",
    "Ebm",
    "Em",
    "Fm",
    "F#m",
    "Gm",
    "G#m",
    "Abm",
    "Am",
    "A#m",
    "Bbm",
    "Bm",
]

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("chordtransposer")

STATIC_CSS_MAX_AGE = 31_536_000


JS_ENTRY = "main.js"
JS_BUNDLE_FALLBACK = "/static/js/main.js"
JS_ENTRY_LANDING = "landing.js"
JS_BUNDLE_LANDING_FALLBACK = "/static/js/landing.js"


def _compute_css_version():
    """Return a short content hash of the built stylesheet for cache-busting."""
    css_path = Path(__file__).resolve().parent / "static" / "tailwind.css"
    try:
        digest = hashlib.sha256(css_path.read_bytes()).hexdigest()
    except OSError:
        return "dev"
    return digest[:12]


def _resolve_js_bundle(entry=JS_ENTRY, fallback=JS_BUNDLE_FALLBACK):
    """Return the hashed frontend entry URL from Vite's build manifest.

    Falls back to an unhashed path when the manifest is unavailable so the
    templates still render during development before a build has run.
    """
    manifest_path = Path(__file__).resolve().parent / "static" / "js" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError):
        return fallback
    resolved = manifest.get(entry)
    if not resolved or "file" not in resolved:
        return fallback
    return f"/static/js/{resolved['file']}"


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

CSS_VERSION = _compute_css_version()
JS_BUNDLE = _resolve_js_bundle()
JS_BUNDLE_LANDING = _resolve_js_bundle(JS_ENTRY_LANDING, JS_BUNDLE_LANDING_FALLBACK)


@app.context_processor
def inject_asset_versions():
    """Expose the stylesheet and script cache-busting references to templates."""
    return {
        "css_version": CSS_VERSION,
        "js_bundle": JS_BUNDLE,
        "js_bundle_landing": JS_BUNDLE_LANDING,
    }


logger.info(
    "app initialised: port=%s gotenberg_url_set=%s",
    os.environ.get("PORT", "8080"),
    bool(os.environ.get("GOTENBERG_URL")),
)


@app.before_request
def log_request_start():
    """Log the method, path and client for every incoming request."""
    logger.info("--> %s %s from %s", request.method, request.path, request.remote_addr)


@app.after_request
def log_request_end(response):
    """Log the status code returned for every request."""
    logger.info("<-- %s %s %s", request.method, request.path, response.status_code)
    return response


@app.after_request
def set_cache_headers(response):
    """Cache versioned static assets aggressively and always revalidate HTML pages."""
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = f"public, max-age={STATIC_CSS_MAX_AGE}, immutable"
    elif response.mimetype == "text/html":
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.route("/")
def index():
    """Render the upload page with available key options."""
    return render_template(
        "index.html",
        keys=KEY_OPTIONS,
        max_semitones=MAX_SEMITONES,
        faq_items=FAQ_ITEMS,
        howto_steps=HOWTO_STEPS,
        chart=seo.compact_chromatic_chart(),
        nav_sections=seo.nav_sections(),
        current_path="/",
        jsonld=seo.home_jsonld(),
    )


@app.route("/health")
def health():
    """Return a lightweight liveness response for container health checks."""
    return jsonify({"status": "ok"})


@app.route("/robots.txt")
def robots():
    """Serve robots.txt allowing all crawlers and pointing to the sitemap."""
    body = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.route("/favicon.svg")
def favicon():
    """Serve the SVG favicon."""
    return app.send_static_file("favicon.svg")


@app.route("/og-image.png")
def og_image():
    """Serve the branded social share image used for Open Graph and Twitter cards."""
    return app.send_static_file("og-image.png")


@app.route("/sitemap.xml")
def sitemap():
    """Serve a sitemap generated from the home page and every landing page."""
    urls = []
    for path in seo.sitemap_paths():
        priority = "1.0" if path == "/" else "0.8"
        urls.append(
            f"  <url><loc>{SITE_URL}{path}</loc><changefreq>monthly</changefreq>"
            f"<priority>{priority}</priority></url>"
        )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    return Response(body, mimetype="application/xml")


@app.route("/transpose", methods=["POST"])
def transpose():
    """Transpose an uploaded .docx and return the generated file as a download."""
    uploaded = request.files.get("file")
    current_key = (request.form.get("current_key") or "").strip()
    target_key = (request.form.get("target_key") or "").strip()
    output_format = (request.form.get("format") or "docx").strip().lower()

    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "Please choose a .docx file to upload."}), 400
    if not uploaded.filename.lower().endswith(".docx"):
        return jsonify({"error": "Only .docx files are supported."}), 400
    if not current_key or not target_key:
        return jsonify({"error": "Both current and desired keys are required."}), 400
    if output_format not in ("docx", "pdf"):
        return jsonify({"error": "Unsupported output format."}), 400

    file_bytes = uploaded.read()
    if not file_bytes:
        return jsonify({"error": "The uploaded file is empty."}), 400

    try:
        docx_bytes, from_label, to_label, changes = transpose_document_bytes(
            file_bytes, current_key, target_key
        )
    except InvalidKeyError as exc:
        return jsonify({"error": str(exc)}), 400
    except (PackageNotFoundError, BadZipFile):
        return jsonify({"error": "Could not read the file as a valid .docx document."}), 400

    stem = uploaded.filename.rsplit(".", 1)[0]

    if output_format == "pdf":
        try:
            output_bytes = convert_docx_to_pdf(docx_bytes)
        except PdfConversionError as exc:
            return jsonify({"error": str(exc)}), 503
        mimetype = PDF_MIMETYPE
        download_name = f"{stem}_{to_label}.pdf"
    else:
        output_bytes = docx_bytes
        mimetype = DOCX_MIMETYPE
        download_name = f"{stem}_{to_label}.docx"

    changes_header = ", ".join(f"{a}->{b}" for a, b in changes) if changes else "none"

    response = send_file(
        BytesIO(output_bytes),
        mimetype=mimetype,
        as_attachment=True,
        download_name=download_name,
    )
    response.headers["X-Transpose-From"] = quote(from_label)
    response.headers["X-Transpose-To"] = quote(to_label)
    response.headers["X-Transpose-Changes"] = quote(changes_header)
    return response


LANDING_PAGES = seo.landing_pages()
NAV_SECTIONS = seo.nav_sections()


def _landing_context(page):
    """Return the template context for a single landing page."""
    return {
        "page": page,
        "keys": KEY_OPTIONS,
        "max_semitones": MAX_SEMITONES,
        "preselect_from": page["preselect_from"],
        "preselect_to": page["preselect_to"],
        "faq_items": FAQ_ITEMS,
        "nav_sections": NAV_SECTIONS,
        "current_path": page["path"],
        "page_title": page["title"],
        "page_description": page["description"],
        "canonical_url": page["canonical"],
        "jsonld": page["jsonld"],
    }


def _make_landing_view(page):
    """Return a view function rendering the shared landing template for a page."""

    def landing_view():
        return render_template("landing.html", **_landing_context(page))

    return landing_view


for _landing_page in LANDING_PAGES:
    app.add_url_rule(
        _landing_page["path"],
        f"landing_{_landing_page['id']}",
        _make_landing_view(_landing_page),
    )


if __name__ == "__main__":
    debug_enabled = os.environ.get("FLASK_DEBUG") == "1"
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=debug_enabled,
    )
