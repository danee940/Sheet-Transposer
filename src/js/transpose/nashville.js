import {
  CHORD_TOKEN_RE,
  isChordToken,
  ROOT_MATCH_RE,
  splitAffixes,
} from "./chords.js";
import { mod12, noteSemitone } from "./notation.js";

const MAJOR_SCALE_DEGREES = { 0: "1", 2: "2", 4: "3", 5: "4", 7: "5", 9: "6", 11: "7" };
const CHROMATIC_DEGREE_NAMES = { 1: "b2", 3: "b3", 6: "b5", 8: "b6", 10: "b7" };

const CHORDPRO_BRACKET_RE = /\[([^\]]+)\]/g;

export function noteToNashvilleDegree(note, tonicSemitone, german) {
  const degree = mod12(noteSemitone(note, german) - tonicSemitone);
  if (degree in MAJOR_SCALE_DEGREES) return MAJOR_SCALE_DEGREES[degree];
  return CHROMATIC_DEGREE_NAMES[degree];
}

export function chordToNashville(chord, tonicSemitone, german) {
  const { leading, core, trailing } = splitAffixes(chord);
  if (core !== chord) {
    if (!CHORD_TOKEN_RE.test(core)) return chord;
    return leading + chordToNashville(core, tonicSemitone, german) + trailing;
  }

  const match = ROOT_MATCH_RE.exec(chord);
  if (!match) return chord;
  const root = match[1];
  const remainder = match[2];
  const number = noteToNashvilleDegree(root, tonicSemitone, german);

  const slashIndex = remainder.indexOf("/");
  if (slashIndex !== -1) {
    const beforeSlash = remainder.slice(0, slashIndex);
    const bass = remainder.slice(slashIndex + 1);
    const bassMatch = ROOT_MATCH_RE.exec(bass);
    if (bassMatch) {
      const bassNumber = noteToNashvilleDegree(bassMatch[1], tonicSemitone, german);
      return number + beforeSlash + "/" + bassNumber + bassMatch[2];
    }
  }
  return number + remainder;
}

export function nashvilleLine(line, tonicSemitone, german) {
  const stripped = line.replace(/^\s+/, "");
  const leading = line.slice(0, line.length - stripped.length);
  let result = leading;

  const tokenSplit = /(\S+)(\s*)/g;
  let match;
  while ((match = tokenSplit.exec(line.slice(leading.length))) !== null) {
    let token = match[1];
    const trailing = match[2];
    if (isChordToken(token)) token = chordToNashville(token, tonicSemitone, german);
    result += token + trailing;
  }
  return result;
}

export function nashvilleChordProLine(line, tonicSemitone, german) {
  return line.replace(CHORDPRO_BRACKET_RE, (whole, token) => {
    if (!CHORD_TOKEN_RE.test(token.trim())) return whole;
    return `[${chordToNashville(token, tonicSemitone, german)}]`;
  });
}
