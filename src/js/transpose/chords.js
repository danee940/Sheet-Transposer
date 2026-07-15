import { GERMAN_NOTE_NAMES, transposeNote } from "./notation.js";

export const ROOT_PATTERN = "(?:Cis|Des|Dis|Eis|Fis|Ges|Gis|Ais|His|Ces|Fes|Es|As|[A-Ha-h](?:#|b)?)";
export const QUALITY_PATTERN = "(?:maj|min|dim|aug|sus|add|m|M|\\+|°|ø|\\d|#|b|-|\\(|\\)|,)*";

export const CHORD_TOKEN_RE = new RegExp(
  `^${ROOT_PATTERN}${QUALITY_PATTERN}(?:/${ROOT_PATTERN}${QUALITY_PATTERN})?$`
);
export const ROOT_MATCH_RE = new RegExp(`^(${ROOT_PATTERN})([\\s\\S]*)$`);

export const PUNCTUATION = "().,;:…\"'-";

export class ChangeSet {
  constructor() {
    this.entries = new Map();
  }

  add(original, transposed) {
    this.entries.set(`${original}\u0000${transposed}`, [original, transposed]);
  }

  sorted() {
    return [...this.entries.values()].sort((a, b) => {
      if (a[0] !== b[0]) return a[0] < b[0] ? -1 : 1;
      if (a[1] !== b[1]) return a[1] < b[1] ? -1 : 1;
      return 0;
    });
  }
}

const LINE_BREAK_RE = /\r\n|[\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]/g;
const WHITESPACE_RE = /\s+/;

export function splitLinesKeepEnds(text) {
  const segments = [];
  let last = 0;
  LINE_BREAK_RE.lastIndex = 0;
  let match;
  while ((match = LINE_BREAK_RE.exec(text)) !== null) {
    segments.push({ content: text.slice(last, match.index), ending: match[0] });
    last = LINE_BREAK_RE.lastIndex;
  }
  if (last < text.length) {
    segments.push({ content: text.slice(last), ending: "" });
  }
  return segments;
}

export function splitLineContents(text) {
  return splitLinesKeepEnds(text).map((segment) => segment.content);
}

function splitWhitespace(text) {
  return text.split(WHITESPACE_RE).filter((token) => token.length > 0);
}

function leadingWhitespace(text) {
  const stripped = text.replace(/^\s+/, "");
  return text.slice(0, text.length - stripped.length);
}

function stripChars(text, chars) {
  let start = 0;
  while (start < text.length && chars.includes(text[start])) start += 1;
  let end = text.length;
  while (end > start && chars.includes(text[end - 1])) end -= 1;
  return text.slice(start, end);
}

export function splitAffixes(token) {
  let start = 0;
  while (start < token.length && PUNCTUATION.includes(token[start])) start += 1;
  let end = token.length;
  while (end > start && PUNCTUATION.includes(token[end - 1])) end -= 1;
  return { leading: token.slice(0, start), core: token.slice(start, end), trailing: token.slice(end) };
}

export function transposeChord(chord, semitones, spelling, german) {
  const { leading, core, trailing } = splitAffixes(chord);
  if (core !== chord) {
    if (!CHORD_TOKEN_RE.test(core)) return chord;
    return leading + transposeChord(core, semitones, spelling, german) + trailing;
  }

  const match = ROOT_MATCH_RE.exec(chord);
  if (!match) return chord;
  const root = match[1];
  const remainder = match[2];
  const newRoot = transposeNote(root, semitones, spelling, german);

  const slashIndex = remainder.indexOf("/");
  if (slashIndex !== -1) {
    const beforeSlash = remainder.slice(0, slashIndex);
    const bass = remainder.slice(slashIndex + 1);
    const bassMatch = ROOT_MATCH_RE.exec(bass);
    if (bassMatch) {
      const newBass = transposeNote(bassMatch[1], semitones, spelling, german);
      return newRoot + beforeSlash + "/" + newBass + bassMatch[2];
    }
  }
  return newRoot + remainder;
}

export function isChordToken(token) {
  const core = stripChars(token, PUNCTUATION);
  return core !== "" && CHORD_TOKEN_RE.test(core);
}

function isUpper(text) {
  return text !== text.toLowerCase() && text === text.toUpperCase();
}

function isDecoration(token) {
  const { core } = splitAffixes(token);
  if (core === "") return true;
  if (core.endsWith(":") || token.includes(":")) return true;
  return isUpper(core);
}

export function isChordLine(text) {
  const tokens = splitWhitespace(text);
  if (tokens.length === 0) return false;
  let chordCount = 0;
  for (const token of tokens) {
    if (isChordToken(token)) {
      chordCount += 1;
    } else if (!isDecoration(token)) {
      return false;
    }
  }
  return chordCount > 0;
}

const GERMAN_ONLY_ROOTS = new Set(
  Object.keys(GERMAN_NOTE_NAMES)
    .filter((name) => name.length > 1)
    .map((name) => name.toUpperCase())
);
GERMAN_ONLY_ROOTS.add("H");

function* tokenRoots(token) {
  const { core } = splitAffixes(token);
  for (const part of core.split("/")) {
    const match = ROOT_MATCH_RE.exec(part);
    if (match) yield match[1];
  }
}

export function lineUsesGerman(text) {
  for (const token of splitWhitespace(text)) {
    for (const root of tokenRoots(token)) {
      if (GERMAN_ONLY_ROOTS.has(root.toUpperCase())) return true;
    }
  }
  return false;
}

export function transposeLineText(text, semitones, spelling, german, changes) {
  const leading = leadingWhitespace(text);
  const body = text.slice(leading.length);
  let result = leading;

  const tokenSplit = /(\S+)(\s*)/g;
  let match;
  while ((match = tokenSplit.exec(body)) !== null) {
    const chord = match[1];
    let trailing = match[2];
    let transposed;
    if (isChordToken(chord)) {
      transposed = transposeChord(chord, semitones, spelling, german);
    } else {
      transposed = chord;
    }
    if (transposed !== chord) changes.add(chord, transposed);

    const diff = transposed.length - chord.length;
    if (diff > 0) {
      trailing = trailing.slice(Math.min(diff, trailing.length));
    } else if (diff < 0) {
      trailing = trailing + " ".repeat(-diff);
    }
    result += transposed + trailing;
  }

  return result;
}
