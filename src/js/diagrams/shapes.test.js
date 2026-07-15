import { describe, expect, it } from "vitest";

import { chordNotes, classifyQuality, lookupShape, parseChordSymbol } from "./shapes.js";

function guitarFrets(symbol) {
  const shape = lookupShape(parseChordSymbol(symbol), "guitar");
  return shape === null ? null : shape.frets;
}

describe("classifyQuality", () => {
  const cases = [
    ["", "maj"],
    ["m", "min"],
    ["min", "min"],
    ["maj7", "maj7"],
    ["M7", "maj7"],
    ["m7", "min7"],
    ["7", "dom7"],
    ["dim", "dim"],
    ["°", "dim"],
    ["dim7", "dim7"],
    ["m7b5", "min7b5"],
    ["ø", "min7b5"],
    ["aug", "aug"],
    ["+", "aug"],
    ["sus2", "sus2"],
    ["sus4", "sus4"],
    ["sus", "sus4"],
    ["6", "maj6"],
    ["m6", "min6"],
    ["9", "dom9"],
    ["add9", "add9"],
  ];
  for (const [quality, expected] of cases) {
    it(`classifies ${JSON.stringify(quality)} as ${expected}`, () => {
      expect(classifyQuality(quality)).toBe(expected);
    });
  }
});

describe("guitar open-chord lookups", () => {
  const expected = {
    C: [-1, 3, 2, 0, 1, 0],
    D: [-1, -1, 0, 2, 3, 2],
    E: [0, 2, 2, 1, 0, 0],
    G: [3, 2, 0, 0, 0, 3],
    A: [-1, 0, 2, 2, 2, 0],
    Am: [-1, 0, 2, 2, 1, 0],
    Em: [0, 2, 2, 0, 0, 0],
    Dm: [-1, -1, 0, 2, 3, 1],
    E7: [0, 2, 0, 1, 0, 0],
    Am7: [-1, 0, 2, 0, 1, 0],
    Cmaj7: [-1, 3, 2, 0, 0, 0],
  };
  for (const [symbol, frets] of Object.entries(expected)) {
    it(`returns the expected shape for ${symbol}`, () => {
      expect(guitarFrets(symbol)).toEqual(frets);
    });
  }
});

describe("guitar movable barre fallbacks", () => {
  it("builds an E-shape barre for F#", () => {
    expect(guitarFrets("F#")).toEqual([2, 4, 4, 3, 2, 2]);
  });

  it("builds an A-shape barre for Bb", () => {
    expect(guitarFrets("Bb")).toEqual([-1, 1, 3, 3, 3, 1]);
  });

  it("builds a minor barre for Cm", () => {
    expect(guitarFrets("Cm")).toEqual([-1, 3, 5, 5, 4, 3]);
  });
});

describe("graceful fallback for unsupported fretted qualities", () => {
  it("returns null for a guitar diminished chord", () => {
    expect(guitarFrets("Cdim")).toBeNull();
  });

  it("still resolves the same chord on piano", () => {
    const shape = lookupShape(parseChordSymbol("Cdim"), "piano");
    expect(shape.kind).toBe("piano");
  });
});

describe("ukulele lookups", () => {
  it("returns the open C shape", () => {
    const shape = lookupShape(parseChordSymbol("C"), "ukulele");
    expect(shape.frets).toEqual([0, 0, 0, 3]);
  });
});

describe("piano and note spelling", () => {
  it("returns chord tones for a C major triad", () => {
    const shape = lookupShape(parseChordSymbol("C"), "piano");
    expect(shape.kind).toBe("piano");
    expect(chordNotes(parseChordSymbol("C"))).toEqual(["C", "E", "G"]);
  });

  it("includes the slash bass note", () => {
    expect(chordNotes(parseChordSymbol("C/G"))).toContain("G");
  });

  it("spells a German H chord as B natural", () => {
    const chord = parseChordSymbol("H", true);
    expect(chord.rootSemitone).toBe(11);
  });

  it("rejects non-chord tokens", () => {
    expect(parseChordSymbol("Chorus:")).toBeNull();
  });
});
