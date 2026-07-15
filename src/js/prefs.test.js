import { describe, expect, it } from "vitest";

import { sanitizePrefs } from "./prefs.js";

describe("sanitizePrefs", () => {
  it("keeps only the allowed preference keys", () => {
    const clean = sanitizePrefs({
      mode: "key",
      currentKey: "C",
      targetKey: "D",
      semitones: 2,
      notation: "flat",
      instrument: "guitar",
      chordText: "C G Am F",
      lyrics: "secret verse",
    });
    expect(clean).toEqual({
      mode: "key",
      currentKey: "C",
      targetKey: "D",
      semitones: 2,
      notation: "flat",
      instrument: "guitar",
    });
    expect(clean).not.toHaveProperty("chordText");
    expect(clean).not.toHaveProperty("lyrics");
  });

  it("drops non-primitive values", () => {
    expect(sanitizePrefs({ currentKey: { nested: true }, targetKey: ["D"] })).toEqual({});
  });

  it("returns an empty object for non-object input", () => {
    expect(sanitizePrefs(null)).toEqual({});
    expect(sanitizePrefs("string")).toEqual({});
  });
});
