"""Transpose chord sheets in .docx format between musical keys."""

import re
import sys
from io import BytesIO
from pathlib import Path

from docx import Document

INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "output"

NOTE_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "Fb": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "Cb": 11,
    "B#": 0,
    "H": 11,
    "H#": 0,
}

GERMAN_NOTE_TO_SEMITONE = dict(NOTE_TO_SEMITONE)
GERMAN_NOTE_TO_SEMITONE["B"] = 10
GERMAN_NOTE_TO_SEMITONE["Bb"] = 9

SHARP_KEYS = {"G", "D", "A", "E", "B", "F#", "C#", "Em", "Bm", "F#m", "C#m", "G#m", "D#m", "A#m"}
FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm", "Abm"}

SHARP_SPELLING = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_SPELLING = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

GERMAN_SHARP_SPELLING = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "B", "H"]
GERMAN_FLAT_SPELLING = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "B", "H"]

ROOT_PATTERN = r"[A-Ha-h](?:#|b)?"
QUALITY_PATTERN = r"(?:maj|min|dim|aug|sus|add|m|M|\+|°|ø|\d|#|b|-|\(|\)|,)*"
CHORD_TOKEN_RE = re.compile(
    rf"^{ROOT_PATTERN}{QUALITY_PATTERN}(?:/{ROOT_PATTERN}{QUALITY_PATTERN})?$"
)
ROOT_MATCH_RE = re.compile(rf"^({ROOT_PATTERN})(.*)$")
TOKEN_SPLIT_RE = re.compile(r"(\S+)(\s*)")


def parse_key(raw):
    """Parse a raw key string into a (note, is_minor) tuple, or None if invalid."""
    text = raw.strip()
    if not text:
        return None
    root = text[0].upper()
    rest = text[1:]
    accidental = ""
    if rest and rest[0] in "#b":
        accidental = rest[0]
        rest = rest[1:]
    note = root + accidental
    if note not in NOTE_TO_SEMITONE:
        return None
    minor = rest.strip().lower() in ("m", "min", "minor")
    return note, minor


def key_label(note, minor):
    """Return the key label string, appending 'm' for minor keys."""
    return note + ("m" if minor else "")


def prefers_flats(target_note, target_minor):
    """Return True if the target key conventionally uses flat spelling."""
    label = key_label(target_note, target_minor)
    if label in FLAT_KEYS or target_note in FLAT_KEYS:
        return True
    if label in SHARP_KEYS or target_note in SHARP_KEYS:
        return False
    return True


def choose_spelling(use_flats, german):
    """Return the appropriate chromatic spelling list for the given preferences."""
    if german:
        return GERMAN_FLAT_SPELLING if use_flats else GERMAN_SHARP_SPELLING
    return FLAT_SPELLING if use_flats else SHARP_SPELLING


def note_semitone(note, german):
    """Return the semitone index (0–11) for a note name."""
    key = note[0].upper() + note[1:]
    table = GERMAN_NOTE_TO_SEMITONE if german else NOTE_TO_SEMITONE
    return table[key]


def transpose_note(note, semitones, spelling, german):
    """Transpose a single note name by the given number of semitones."""
    semitone = (note_semitone(note, german) + semitones) % 12
    return spelling[semitone]


def transpose_chord(chord, semitones, spelling, german):
    """Transpose a chord symbol (including optional bass note) by semitones."""
    match = ROOT_MATCH_RE.match(chord)
    if not match:
        return chord
    root, remainder = match.group(1), match.group(2)
    new_root = transpose_note(root, semitones, spelling, german)
    if "/" in remainder:
        before_slash, bass = remainder.split("/", 1)
        bass_match = ROOT_MATCH_RE.match(bass)
        if bass_match:
            new_bass = transpose_note(bass_match.group(1), semitones, spelling, german)
            return new_root + before_slash + "/" + new_bass + bass_match.group(2)
    return new_root + remainder


def is_chord_line(text):
    """Return True if every whitespace-separated token in text is a valid chord symbol."""
    tokens = text.split()
    if not tokens:
        return False
    return all(CHORD_TOKEN_RE.match(token) for token in tokens)


def line_uses_german(text):
    """Return True if the line contains any German-notation note (H)."""
    for token in text.split():
        match = ROOT_MATCH_RE.match(token)
        if match and match.group(1).upper().startswith("H"):
            return True
        if "/H" in token or token.startswith("H"):
            return True
    return False


def transpose_line_text(text, semitones, spelling, german, changes):
    """Transpose all chord tokens in a line, preserving spacing, and record changes."""
    leading = text[: len(text) - len(text.lstrip())]
    body = text[len(leading) :]
    result = leading

    for token_match in TOKEN_SPLIT_RE.finditer(body):
        chord = token_match.group(1)
        trailing = token_match.group(2)
        transposed = transpose_chord(chord, semitones, spelling, german)
        if transposed != chord:
            changes.add((chord, transposed))

        diff = len(transposed) - len(chord)
        if diff > 0:
            trailing = trailing[min(diff, len(trailing)) :]
        elif diff < 0:
            trailing = trailing + " " * (-diff)
        result += transposed + trailing

    return result


def redistribute_to_runs(paragraph, new_text):
    """Write new_text into the paragraph's runs, concentrating text in the styled run."""
    runs = [run for run in paragraph.runs if run.text != ""]
    if not runs:
        return

    styled_run = _pick_styled_run(runs)
    for run in runs:
        run.text = new_text if run is styled_run else ""


def _pick_styled_run(runs):
    """Return the first run with non-whitespace text, falling back to the first run."""
    for run in runs:
        if run.text.strip():
            return run
    return runs[0]


def process_paragraph(paragraph, semitones, use_flats, german, changes):
    """Transpose all chords in a paragraph if it is a chord line."""
    text = paragraph.text
    if not is_chord_line(text):
        return
    spelling = choose_spelling(use_flats, german)
    new_text = transpose_line_text(text, semitones, spelling, german, changes)
    redistribute_to_runs(paragraph, new_text)


def iter_paragraphs(document):
    """Yield every paragraph in the document, including tables, headers, and footers."""
    yield from document.paragraphs
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs
    for section in document.sections:
        for container in (section.header, section.footer):
            yield from container.paragraphs


def detect_german(document):
    """Return True if any chord line in the document uses German note notation."""
    for paragraph in iter_paragraphs(document):
        text = paragraph.text
        if is_chord_line(text) and line_uses_german(text):
            return True
    return False


def find_input_file():
    """Return the first .docx file in INPUT_DIR, or None if none exists."""
    docx_files = [p for p in INPUT_DIR.glob("*.docx") if not p.name.startswith("~$")]
    if not docx_files:
        return None
    return docx_files[0]


def _prompt_key(prompt_text):
    """Prompt the user for a key string, parse it, and exit on invalid input."""
    raw = input(prompt_text)
    parsed = parse_key(raw)
    if parsed is None:
        print(f"'{raw.strip()}' is not a valid key.")
        sys.exit(1)
    return parsed


def _transpose_document(document, semitones, use_flats, german):
    """Apply transposition to every paragraph in the document and return the change set."""
    changes: set[tuple[str, str]] = set()
    for paragraph in iter_paragraphs(document):
        process_paragraph(paragraph, semitones, use_flats, german, changes)
    return changes


def _save_and_report(document, input_file, from_label, to_label, changes):
    """Save the transposed document and print a summary of chord changes."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{input_file.stem}_{to_label}.docx"
    document.save(output_file)

    print(f"\nSheet transposed from {from_label} to {to_label}\n")
    if changes:
        for original, transposed in sorted(changes):
            print(f"{original} -> {transposed}")
    else:
        print("No chords were changed.")
    print(f"\nSaved to: {output_file}")


class InvalidKeyError(ValueError):
    """Raised when a supplied key string cannot be parsed."""


def transpose_document_bytes(file_bytes, current_key, target_key):
    """Transpose a .docx given as bytes and return (docx_bytes, from_label, to_label, changes)."""
    current = parse_key(current_key)
    if current is None:
        raise InvalidKeyError(f"'{current_key}' is not a valid key.")
    target = parse_key(target_key)
    if target is None:
        raise InvalidKeyError(f"'{target_key}' is not a valid key.")

    current_note, current_minor = current
    target_note, target_minor = target

    document = Document(BytesIO(file_bytes))
    german = detect_german(document)

    semitones = (note_semitone(target_note, german) - note_semitone(current_note, german)) % 12
    use_flats = prefers_flats(target_note, target_minor)

    changes = _transpose_document(document, semitones, use_flats, german)

    from_label = key_label(current_note, current_minor)
    to_label = key_label(target_note, target_minor)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)

    return buffer.getvalue(), from_label, to_label, sorted(changes)


def main():
    """Entry point: load the input file, prompt for keys, transpose, and save."""
    input_file = find_input_file()
    if input_file is None:
        print(f"No .docx file found in {INPUT_DIR}. Drop your sheet there first.")
        sys.exit(1)

    print(f"Found input file: {input_file.name}\n")

    current_note, current_minor = _prompt_key("Current key of the sheet (e.g. C, Am, F#): ")
    target_note, target_minor = _prompt_key("Desired key to transpose to (e.g. D, Bm, Eb): ")

    document = Document(str(input_file))
    german = detect_german(document)

    semitones = (note_semitone(target_note, german) - note_semitone(current_note, german)) % 12
    use_flats = prefers_flats(target_note, target_minor)

    changes = _transpose_document(document, semitones, use_flats, german)

    from_label = key_label(current_note, current_minor)
    to_label = key_label(target_note, target_minor)

    _save_and_report(document, input_file, from_label, to_label, changes)


if __name__ == "__main__":
    main()
