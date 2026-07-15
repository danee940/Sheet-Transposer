"""Data and structured-content helpers for the server-rendered SEO landing pages.

This module is the single source of truth for the FAQ, the how-to steps, the
curated key-pair pages, the instrument pages, and the chromatic transposition
chart. Both the Flask routes and the templates read their content from here so
the visible copy and the JSON-LD structured data cannot drift apart.
"""

from transpose import SHARP_SPELLING, key_semitone, parse_key, transpose_text

SITE_URL = "https://chordtransposer.app"

FAQ_ITEMS = [
    {
        "question": "How do I transpose chords to a different key?",
        "answer": (
            "Paste your chords, choose the key the song is currently in, and pick the key you "
            "want it in. The transposed chords appear instantly, with no upload needed. Every "
            "chord is shifted by the same interval so the song sounds identical, just higher or "
            "lower."
        ),
    },
    {
        "question": "Can I transpose chords without uploading a file?",
        "answer": (
            "Yes. Use the paste-chords mode to type or paste chords directly and see the "
            "transposed result instantly in your browser. Uploading a .docx file is optional and "
            "only needed when you want to download a transposed Word or PDF document."
        ),
    },
    {
        "question": "Does transposing keep my document formatting?",
        "answer": (
            "Yes. Only the chord names are changed. Fonts, spacing, colours, tables, and the "
            "overall layout of your .docx are preserved."
        ),
    },
    {
        "question": "Which chords and keys are supported?",
        "answer": (
            "All twelve major and twelve minor keys are supported, including sharp and flat "
            "spellings such as C#, Db, F#m, and Bbm. Slash chords, sus, add, maj7, and other "
            "chord qualities are recognised and transposed correctly."
        ),
    },
    {
        "question": "Do you support German H notation?",
        "answer": (
            "Yes. German notation where H means B and B means B-flat is detected and transposed "
            "correctly, so sheets written in either the English or German system work."
        ),
    },
    {
        "question": "Is the chord transposer free?",
        "answer": (
            "Yes, it is completely free with no sign-up. You can transpose as many chord sheets "
            "as you like."
        ),
    },
    {
        "question": "Can I download the result as a PDF?",
        "answer": (
            "Yes. Choose the PDF output option before transposing to get a ready-to-print PDF, "
            "or keep the editable .docx version."
        ),
    },
    {
        "question": "Are my files stored anywhere?",
        "answer": (
            "No. Your chord sheet is processed to generate the transposed file and is not kept "
            "after the download is returned."
        ),
    },
]

HOWTO_STEPS = [
    {
        "name": "Add your chords",
        "text": "Paste your chords, or upload a chord sheet in .docx format.",
    },
    {
        "name": "Choose the current key",
        "text": "Select the key the song is currently written in.",
    },
    {
        "name": "Choose the target key",
        "text": "Select the key you want to play it in.",
    },
    {
        "name": "Get the result",
        "text": "See the result instantly, or download it as a .docx or PDF.",
    },
]

WEBAPP_JSONLD = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Chord Transposer",
    "url": f"{SITE_URL}/",
    "description": (
        "Free online tool to transpose chords between musical keys. Paste chords for an "
        "instant preview, or upload a .docx chord sheet to download it transposed with "
        "formatting preserved. Supports standard and German (H) chord notation."
    ),
    "applicationCategory": "MultimediaApplication",
    "operatingSystem": "Any",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
}

CURATED_KEY_PAIRS = [
    ("C", "D"),
    ("C", "G"),
    ("C", "A"),
    ("C", "E"),
    ("C", "F"),
    ("G", "A"),
    ("G", "C"),
    ("G", "E"),
    ("D", "C"),
    ("D", "E"),
    ("D", "G"),
    ("A", "G"),
    ("E", "G"),
    ("E", "D"),
    ("F", "G"),
    ("Bb", "C"),
]

INSTRUMENTS = [
    {
        "instrument": "guitar",
        "slug": "guitar-chord-transposer",
        "name": "Guitar",
        "title": "Guitar Chord Transposer — Change Key & Capo Finder",
        "description": (
            "Transpose guitar chords to any key online and find the capo position that keeps "
            "familiar open-chord shapes. Free, instant, and formatting-preserving for .docx "
            "chord sheets."
        ),
        "h1": "Guitar chord transposer",
        "preselect_from": "C",
        "preselect_to": "G",
        "show_capo": True,
        "intro_paragraphs": [
            "Change the key of any guitar song and keep playing the shapes you already know. "
            "Paste your chords, choose the current and target keys, and every chord moves by the "
            "same interval so the song sounds identical, just higher or lower.",
            "Guitarists often transpose to fit a singer's range or to swap awkward barre chords "
            "for open positions. Pair the transposer with the capo finder below to see which "
            "fret lets you play easy open shapes while sounding in the key you want.",
        ],
        "features": [
            "Recognises slash chords like G/B, plus sus, add, and maj7 qualities.",
            "Works with both sharp and flat spellings such as F# and Db.",
            "Capo finder maps your target key to open-chord shapes.",
        ],
    },
    {
        "instrument": "ukulele",
        "slug": "ukulele-chord-transposer",
        "name": "Ukulele",
        "title": "Ukulele Chord Transposer — Change Chords to Any Key",
        "description": (
            "Transpose ukulele chords to any key instantly. Move a song up or down to suit your "
            "voice while keeping the same easy shapes. Free and no sign-up."
        ),
        "h1": "Ukulele chord transposer",
        "preselect_from": "C",
        "preselect_to": "G",
        "show_capo": False,
        "intro_paragraphs": [
            "Transpose ukulele songs to a more comfortable key in seconds. Paste your chords, "
            "set the current and target keys, and see the whole sheet shift by the same interval "
            "so the melody is unchanged.",
            "Ukulele players lean on friendly keys like C, F, G, and A that sit well under the "
            "fingers. Transposing into one of those keys turns a tricky chart into open, "
            "singable shapes without changing how the song feels.",
        ],
        "features": [
            "Great for moving songs into ukulele-friendly keys such as C, F, and G.",
            "Keeps chord qualities intact, from simple triads to sus and 7th chords.",
            "Instant preview in the browser — nothing to install.",
        ],
    },
    {
        "instrument": "piano",
        "slug": "piano-chord-transposer",
        "name": "Piano",
        "title": "Piano Chord Transposer — Transpose Chords to Any Key",
        "description": (
            "Transpose piano and keyboard chords to any key online. Get correct sharp or flat "
            "spellings for the target key instantly, with no sign-up."
        ),
        "h1": "Piano chord transposer",
        "preselect_from": "C",
        "preselect_to": "D",
        "show_capo": False,
        "intro_paragraphs": [
            "Move a piano chart to any key and let the tool handle the spelling. Paste your "
            "chords, pick the current and target keys, and each chord is rewritten with the "
            "sharps or flats that read naturally in the new key.",
            "Pianists transpose to match a vocalist or to trade a key full of black notes for "
            "one that lies more comfortably under the hands. Because there is no capo on a "
            "keyboard, choosing the right written key is what makes a song easier to play.",
        ],
        "features": [
            "Chooses sharp or flat spelling to match the target key.",
            "Handles extended chords, slash chords, and inversions.",
            "Download transposed .docx or PDF chord sheets with layout preserved.",
        ],
    },
]

_INTERVAL_NAMES = {
    1: "a semitone",
    2: "a whole step",
    3: "a minor third",
    4: "a major third",
    5: "a perfect fourth",
    6: "a tritone",
    7: "a perfect fifth",
    8: "a minor sixth",
    9: "a major sixth",
    10: "a minor seventh",
    11: "a major seventh",
}

_EXAMPLE_CHORDS = ["C", "F", "G", "Am"]

COMPACT_CHART_SHIFTS = [2, 5, 7]

_SHIFT_LABELS = {
    2: "+2 (whole step)",
    5: "+5 (fourth)",
    7: "+7 (fifth)",
}


def _key_slug(key):
    """Return the lowercase URL fragment for a key such as 'bb' for 'Bb'."""
    return key.replace("#", "-sharp").lower()


def _semitone_delta(from_key, to_key):
    """Return the upward semitone distance (0-11) between two major keys."""
    from_note, _ = parse_key(from_key)
    to_note, _ = parse_key(to_key)
    return (key_semitone(to_note, False) - key_semitone(from_note, False)) % 12


def _capo_suggestion(from_key, to_key, delta_up):
    """Return a guitar capo tip for moving from one key to another."""
    if delta_up == 0:
        return "no capo is needed because the keys are the same"
    if delta_up <= 7:
        return (
            f"clamp a capo on fret {delta_up} and keep playing {from_key} shapes to sound in "
            f"{to_key}"
        )
    down = 12 - delta_up
    return (
        f"a capo only raises pitch, so either transpose down {down} semitones on paper or play "
        f"{to_key} shapes directly"
    )


def _example_progression(target_key):
    """Return the I-IV-V-vi progression spelled for a key, joined for prose."""
    return " – ".join(
        transpose_text(chord, "C", target_key)[0].strip() for chord in _EXAMPLE_CHORDS
    )


def _breadcrumbs(title, path):
    """Return the breadcrumb trail from the home page to the given landing page."""
    return [
        {"name": "Home", "url": f"{SITE_URL}/"},
        {"name": title, "url": f"{SITE_URL}{path}"},
    ]


def _howto_jsonld(name):
    """Return a HowTo structured-data block built from the shared steps."""
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
        "step": [
            {
                "@type": "HowToStep",
                "position": index,
                "name": step["name"],
                "text": step["text"],
            }
            for index, step in enumerate(HOWTO_STEPS, start=1)
        ],
    }


def _faq_jsonld():
    """Return a FAQPage structured-data block built from the shared FAQ list."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in FAQ_ITEMS
        ],
    }


def _breadcrumb_jsonld(breadcrumbs):
    """Return a BreadcrumbList structured-data block for a landing page."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": crumb["name"],
                "item": crumb["url"],
            }
            for index, crumb in enumerate(breadcrumbs, start=1)
        ],
    }


def home_jsonld():
    """Return the structured-data blocks for the home page."""
    return [WEBAPP_JSONLD, _howto_jsonld("How to transpose chords"), _faq_jsonld()]


def _key_pair_page(from_key, to_key):
    """Build the full page record for a curated key-pair landing page."""
    delta_up = _semitone_delta(from_key, to_key)
    down = 12 - delta_up
    interval = _INTERVAL_NAMES[delta_up]
    example_from = _example_progression(from_key)
    example_to = _example_progression(to_key)

    if delta_up <= 6:
        direction = (
            f"That raises every chord by {interval} ({delta_up} semitones up), a common move "
            f"when the original sits a little low for the singer."
        )
    else:
        direction = (
            f"That is {interval} up ({delta_up} semitones), or the same as moving {down} "
            f"semitones down — handy when {from_key} sits too high to sing comfortably."
        )

    path = f"/transpose/{_key_slug(from_key)}-to-{_key_slug(to_key)}"
    title = f"Transpose {from_key} to {to_key} — Chord Transposer"
    intro_paragraphs = [
        f"Moving a song from {from_key} to {to_key} shifts every chord by the same interval so "
        f"the melody is untouched. {direction}",
        f"On guitar, {_capo_suggestion(from_key, to_key, delta_up)}. As a quick check, a "
        f"I–IV–V–vi progression that reads {example_from} in {from_key} becomes {example_to} in "
        f"{to_key}.",
    ]
    breadcrumbs = _breadcrumbs(f"{from_key} to {to_key}", path)
    return {
        "id": f"transpose_{_key_slug(from_key)}_to_{_key_slug(to_key)}".replace("-", "_"),
        "path": path,
        "kind": "pair",
        "title": title,
        "description": (
            f"Transpose chords from {from_key} to {to_key} online and free. Shift a full chord "
            f"sheet up by {interval} instantly, with a capo tip and worked example."
        ),
        "h1": f"Transpose chords from {from_key} to {to_key}",
        "intro_paragraphs": intro_paragraphs,
        "canonical": f"{SITE_URL}{path}",
        "preselect_from": from_key,
        "preselect_to": to_key,
        "delta_up": delta_up,
        "example_from": example_from,
        "example_to": example_to,
        "show_capo": True,
        "breadcrumbs": breadcrumbs,
        "jsonld": [
            _howto_jsonld(f"How to transpose chords from {from_key} to {to_key}"),
            _faq_jsonld(),
            _breadcrumb_jsonld(breadcrumbs),
        ],
    }


def _instrument_page(instrument):
    """Build the full page record for an instrument landing page."""
    path = f"/{instrument['slug']}"
    breadcrumbs = _breadcrumbs(instrument["name"], path)
    return {
        "id": instrument["slug"].replace("-", "_"),
        "path": path,
        "kind": "instrument",
        "instrument": instrument["instrument"],
        "title": instrument["title"],
        "description": instrument["description"],
        "h1": instrument["h1"],
        "intro_paragraphs": instrument["intro_paragraphs"],
        "features": instrument["features"],
        "canonical": f"{SITE_URL}{path}",
        "preselect_from": instrument["preselect_from"],
        "preselect_to": instrument["preselect_to"],
        "show_capo": instrument["show_capo"],
        "breadcrumbs": breadcrumbs,
        "jsonld": [
            _howto_jsonld(f"How to transpose {instrument['instrument']} chords"),
            _faq_jsonld(),
            _breadcrumb_jsonld(breadcrumbs),
        ],
    }


def _chart_rows(shifts):
    """Return chromatic chart rows mapping each note to its shifted spelling."""
    rows = []
    for index, note in enumerate(SHARP_SPELLING):
        cells = [SHARP_SPELLING[(index + shift) % 12] for shift in shifts]
        rows.append({"note": note, "cells": cells})
    return rows


def chromatic_chart(shifts):
    """Return a chromatic transposition chart for the given semitone shifts."""
    headers = [_SHIFT_LABELS.get(shift, f"+{shift}") for shift in shifts]
    return {"shifts": shifts, "headers": headers, "rows": _chart_rows(shifts)}


def compact_chromatic_chart():
    """Return the small chromatic chart embedded on the home page."""
    return chromatic_chart(COMPACT_CHART_SHIFTS)


def _chart_page():
    """Build the full page record for the chromatic transposition chart page."""
    path = "/chromatic-chart"
    breadcrumbs = _breadcrumbs("Chromatic chart", path)
    return {
        "id": "chromatic_chart",
        "path": path,
        "kind": "chart",
        "title": "Chromatic Transposition Chart — Every Key by Semitone",
        "description": (
            "A chromatic transposition chart showing where each note lands when you shift it up "
            "by one to eleven semitones. Free reference for transposing chords to any key."
        ),
        "h1": "Chromatic transposition chart",
        "intro_paragraphs": [
            "Use this chart to transpose any chord by ear or on paper. Find the row for the note "
            "you have, then read across to the column for the number of semitones you want to "
            "move, and the cell shows the note it becomes.",
            "Every shift applies to all twelve notes equally, so once you know the interval "
            "between your current and target keys you can convert a whole chord sheet a chord at "
            "a time — or paste it into the widget above to do it instantly.",
        ],
        "canonical": f"{SITE_URL}{path}",
        "preselect_from": "C",
        "preselect_to": "D",
        "show_capo": False,
        "chart": chromatic_chart(list(range(1, 12))),
        "breadcrumbs": breadcrumbs,
        "jsonld": [
            _howto_jsonld("How to read the chromatic transposition chart"),
            _faq_jsonld(),
            _breadcrumb_jsonld(breadcrumbs),
        ],
    }


def landing_pages():
    """Return every server-rendered landing page record in navigation order."""
    pages = [_instrument_page(instrument) for instrument in INSTRUMENTS]
    pages.append(_chart_page())
    pages.extend(_key_pair_page(from_key, to_key) for from_key, to_key in CURATED_KEY_PAIRS)
    return pages


def nav_sections():
    """Return grouped internal links for the cross-link hub in nav and footer."""
    instrument_links = [
        {"name": f"{instrument['name']} transposer", "path": f"/{instrument['slug']}"}
        for instrument in INSTRUMENTS
    ]
    pair_links = [
        {
            "name": f"{from_key} to {to_key}",
            "path": f"/transpose/{_key_slug(from_key)}-to-{_key_slug(to_key)}",
        }
        for from_key, to_key in CURATED_KEY_PAIRS
    ]
    reference_links = [{"name": "Chromatic chart", "path": "/chromatic-chart"}]
    return [
        {"heading": "By instrument", "links": instrument_links},
        {"heading": "Popular key changes", "links": pair_links},
        {"heading": "Reference", "links": reference_links},
    ]


def sitemap_paths():
    """Return every indexable path, starting with the home page."""
    return ["/", *[page["path"] for page in landing_pages()]]
