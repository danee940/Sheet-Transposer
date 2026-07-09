"""Flask web frontend for transposing chord sheets in .docx format."""

import os
from io import BytesIO
from urllib.parse import quote

from flask import Flask, jsonify, render_template, request, send_file

from transpose import (
    InvalidKeyError,
    PdfConversionError,
    convert_docx_to_pdf,
    transpose_document_bytes,
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

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

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


@app.route("/")
def index():
    """Render the upload page with available key options."""
    return render_template("index.html", keys=KEY_OPTIONS)


@app.route("/transpose", methods=["POST"])
def transpose():
    """Transpose an uploaded .docx and return the generated file as a download."""
    uploaded = request.files.get("file")
    current_key = (request.form.get("current_key") or "").strip()
    target_key = (request.form.get("target_key") or "").strip()
    output_format = (request.form.get("format") or "docx").strip().lower()

    if uploaded is None or uploaded.filename == "":
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
    except Exception:
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


if __name__ == "__main__":
    debug_enabled = os.environ.get("FLASK_DEBUG") == "1"
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=debug_enabled,
    )
