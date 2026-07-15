"""Tests for the Flask web layer in app.py."""
# pylint: disable=redefined-outer-name,missing-function-docstring

from io import BytesIO
from urllib.parse import unquote

import pytest
from docx import Document

import app as app_module
from app import app

DOCX_MIMETYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def _chord_docx_bytes():
    document = Document()
    document.add_paragraph("C G Am F")
    document.add_paragraph("These are the lyrics")
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _upload(data_bytes, filename="song.docx") -> dict[str, object]:
    return {"file": (BytesIO(data_bytes), filename)}


def test_index_lists_keys(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Chord Transposer" in response.data


def test_index_links_versioned_stylesheet(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "cdn.tailwindcss.com" not in body
    assert f"/static/tailwind.css?v={app_module.CSS_VERSION}" in body


def test_index_html_is_not_cached(client):
    response = client.get("/")
    assert response.headers["Cache-Control"] == "no-cache"


def test_static_css_is_cached_immutably(client):
    response = client.get(f"/static/tailwind.css?v={app_module.CSS_VERSION}")
    assert response.status_code == 200
    cache_control = response.headers["Cache-Control"]
    assert "immutable" in cache_control
    assert f"max-age={app_module.STATIC_CSS_MAX_AGE}" in cache_control


def test_css_version_is_stable_hash():
    assert app_module.CSS_VERSION == app_module._compute_css_version()
    assert len(app_module.CSS_VERSION) == 12


def test_css_version_falls_back_when_missing(monkeypatch):
    def _raise(_self):
        raise OSError("missing")

    monkeypatch.setattr(app_module.Path, "read_bytes", _raise)
    assert app_module._compute_css_version() == "dev"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "Sitemap:" in response.get_data(as_text=True)


def test_og_image_png(client):
    response = client.get("/og-image.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.get_data().startswith(b"\x89PNG")


def test_sitemap_xml(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert "<urlset" in response.get_data(as_text=True)


def test_transpose_missing_file(client):
    response = client.post(
        "/transpose",
        data={"current_key": "C", "target_key": "D"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "choose a .docx" in response.get_json()["error"]


def test_transpose_wrong_extension(client):
    data = _upload(b"not a docx", filename="song.txt")
    data.update({"current_key": "C", "target_key": "D"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Only .docx" in response.get_json()["error"]


def test_transpose_missing_keys(client):
    data = _upload(_chord_docx_bytes())
    data.update({"current_key": "", "target_key": ""})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "keys are required" in response.get_json()["error"]


def test_transpose_unsupported_format(client):
    data = _upload(_chord_docx_bytes())
    data.update({"current_key": "C", "target_key": "D", "format": "txt"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Unsupported output format" in response.get_json()["error"]


def test_transpose_empty_file(client):
    data = _upload(b"", filename="empty.docx")
    data.update({"current_key": "C", "target_key": "D"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "empty" in response.get_json()["error"]


def test_transpose_invalid_key(client):
    data = _upload(_chord_docx_bytes())
    data.update({"current_key": "X", "target_key": "D"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "not a valid key" in response.get_json()["error"]


def test_transpose_invalid_docx(client):
    data = _upload(b"this is not a real docx", filename="bad.docx")
    data.update({"current_key": "C", "target_key": "D"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "valid .docx" in response.get_json()["error"]


def test_transpose_docx_success(client):
    data = _upload(_chord_docx_bytes())
    data.update({"current_key": "C", "target_key": "D"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.mimetype == DOCX_MIMETYPE
    assert "song_D.docx" in response.headers["Content-Disposition"]
    assert unquote(response.headers["X-Transpose-From"]) == "C"
    assert unquote(response.headers["X-Transpose-To"]) == "D"
    assert "C->D" in unquote(response.headers["X-Transpose-Changes"])


def test_transpose_preserves_non_ascii_filename(client):
    data = _upload(_chord_docx_bytes(), filename="Covered-Gizus_rövid_G.docx")
    data.update({"current_key": "C", "target_key": "D"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    disposition = response.headers["Content-Disposition"]
    assert "filename*=UTF-8''Covered-Gizus_r%C3%B6vid_G_D.docx" in disposition


def test_transpose_pdf_success(client, monkeypatch):
    monkeypatch.setattr(app_module, "convert_docx_to_pdf", lambda docx_bytes: b"%PDF-1.4 fake")

    data = _upload(_chord_docx_bytes())
    data.update({"current_key": "C", "target_key": "D", "format": "pdf"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert "song_D.pdf" in response.headers["Content-Disposition"]
    assert response.data == b"%PDF-1.4 fake"


def test_transpose_pdf_conversion_failure(client, monkeypatch):
    def _raise(_docx_bytes):
        raise app_module.PdfConversionError("PDF conversion timed out.")

    monkeypatch.setattr(app_module, "convert_docx_to_pdf", _raise)

    data = _upload(_chord_docx_bytes())
    data.update({"current_key": "C", "target_key": "D", "format": "pdf"})
    response = client.post("/transpose", data=data, content_type="multipart/form-data")

    assert response.status_code == 503
    assert "timed out" in response.get_json()["error"]


def test_transpose_text_success(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C G Am F", "current_key": "C", "target_key": "D"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["text"] == "D A Bm G"
    assert body["from"] == "C"
    assert body["to"] == "D"
    assert {"from": "C", "to": "D"} in body["changes"]


def test_transpose_text_missing_text(client):
    response = client.post(
        "/transpose-text",
        json={"current_key": "C", "target_key": "D"},
    )
    assert response.status_code == 400
    assert "No text" in response.get_json()["error"]


def test_transpose_text_missing_keys(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C G", "current_key": "", "target_key": ""},
    )
    assert response.status_code == 400
    assert "keys are required" in response.get_json()["error"]


def test_transpose_text_invalid_key(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C G", "current_key": "X", "target_key": "D"},
    )
    assert response.status_code == 400
    assert "not a valid key" in response.get_json()["error"]


def test_transpose_text_too_long(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C " * 11_000, "current_key": "C", "target_key": "D"},
    )
    assert response.status_code == 400
    assert "too long" in response.get_json()["error"]


def test_transpose_text_empty_body(client):
    response = client.post("/transpose-text", data=b"", content_type="application/json")
    assert response.status_code == 400
    assert "No text" in response.get_json()["error"]


def test_transpose_text_by_semitones_success(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C G Am F", "semitones": 2},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["text"] == "D A Bm G"
    assert body["semitones"] == 2
    assert body["notation"] == "sharp"
    assert "+2 semitones" in body["label"]
    assert {"from": "C", "to": "D"} in body["changes"]


def test_transpose_text_by_semitones_flat_notation(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C", "semitones": 1, "notation": "flat"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["text"] == "Db"
    assert body["notation"] == "flat"
    assert "♭" in body["label"]


def test_transpose_text_by_semitones_negative_label(client):
    response = client.post(
        "/transpose-text",
        json={"text": "D", "semitones": -1},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["text"] == "C#"
    assert body["label"].startswith("−1 semitone")


def test_transpose_text_by_semitones_zero_label(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C", "semitones": 0},
    )
    assert response.status_code == 200
    assert "No change" in response.get_json()["label"]


def test_transpose_text_by_semitones_rejects_non_integer(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C", "semitones": "2"},
    )
    assert response.status_code == 400
    assert "whole number" in response.get_json()["error"]


def test_transpose_text_by_semitones_rejects_boolean(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C", "semitones": True},
    )
    assert response.status_code == 400
    assert "whole number" in response.get_json()["error"]


def test_transpose_text_by_semitones_rejects_out_of_range(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C", "semitones": 12},
    )
    assert response.status_code == 400
    assert "between" in response.get_json()["error"]


def test_transpose_text_by_semitones_rejects_bad_notation(client):
    response = client.post(
        "/transpose-text",
        json={"text": "C", "semitones": 2, "notation": "double-sharp"},
    )
    assert response.status_code == 400
    assert "sharp" in response.get_json()["error"]


class TestChordProApi:
    def test_key_based_chordpro_keeps_brackets(self, client):
        response = client.post(
            "/transpose-text",
            json={"text": "[C]Amazing [G]grace", "current_key": "C", "target_key": "D"},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["text"] == "[D]Amazing [A]grace"
        assert body["format"] == "chordpro"

    def test_key_based_chordpro_plain_output(self, client):
        response = client.post(
            "/transpose-text",
            json={
                "text": "[C]Amazing [G]grace",
                "current_key": "C",
                "target_key": "D",
                "output_format": "plain",
            },
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["text"] == "D A"
        assert body["format"] == "chordpro"

    def test_key_based_chordpro_invalid_key(self, client):
        response = client.post(
            "/transpose-text",
            json={"text": "[C]x", "current_key": "X", "target_key": "D"},
        )
        assert response.status_code == 400
        assert "not a valid key" in response.get_json()["error"]

    def test_semitone_chordpro_keeps_brackets(self, client):
        response = client.post(
            "/transpose-text",
            json={"text": "[C]Amazing [G]grace", "semitones": 2},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["text"] == "[D]Amazing [A]grace"
        assert body["format"] == "chordpro"

    def test_semitone_chordpro_plain_output(self, client):
        response = client.post(
            "/transpose-text",
            json={"text": "[C]a [G]b", "semitones": 2, "output_format": "plain"},
        )
        assert response.status_code == 200
        assert response.get_json()["text"] == "D A"

    def test_plain_text_has_no_format_field(self, client):
        response = client.post(
            "/transpose-text",
            json={"text": "C G Am F", "current_key": "C", "target_key": "D"},
        )
        assert response.status_code == 200
        assert "format" not in response.get_json()


class TestNashvilleApi:
    def test_converts_chord_line(self, client):
        response = client.post(
            "/nashville-text",
            json={"text": "C G Am F", "tonic_key": "C"},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["text"] == "1 5 6m 4"
        assert body["tonic"] == "C"

    def test_missing_text(self, client):
        response = client.post("/nashville-text", json={"tonic_key": "C"})
        assert response.status_code == 400
        assert "No text" in response.get_json()["error"]

    def test_missing_tonic(self, client):
        response = client.post("/nashville-text", json={"text": "C G"})
        assert response.status_code == 400
        assert "tonic key is required" in response.get_json()["error"]

    def test_invalid_tonic(self, client):
        response = client.post(
            "/nashville-text",
            json={"text": "C G", "tonic_key": "X"},
        )
        assert response.status_code == 400
        assert "not a valid key" in response.get_json()["error"]

    def test_text_too_long(self, client):
        response = client.post(
            "/nashville-text",
            json={"text": "C " * 11_000, "tonic_key": "C"},
        )
        assert response.status_code == 400
        assert "too long" in response.get_json()["error"]

    def test_empty_body(self, client):
        response = client.post("/nashville-text", data=b"", content_type="application/json")
        assert response.status_code == 400
        assert "No text" in response.get_json()["error"]

    def test_chordpro_input(self, client):
        response = client.post(
            "/nashville-text",
            json={"text": "[C]Amazing [G]grace", "tonic_key": "C"},
        )
        assert response.status_code == 200
        assert response.get_json()["text"] == "[1]Amazing [5]grace"
