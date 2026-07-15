import { describe, expect, it } from "vitest";

import {
  autoscrollAtEnd,
  autoscrollStep,
  AUTOSCROLL_DEFAULT_SPEED,
  AUTOSCROLL_MAX_SPEED,
  AUTOSCROLL_MIN_SPEED,
  clampAutoscrollSpeed,
  clampFontSize,
} from "./stage.js";

describe("autoscrollStep", () => {
  it("advances by speed scaled to elapsed time", () => {
    expect(autoscrollStep(0, 60, 1000, 1000)).toBe(60);
    expect(autoscrollStep(100, 60, 500, 1000)).toBe(130);
  });

  it("never scrolls past the maximum", () => {
    expect(autoscrollStep(990, 60, 1000, 1000)).toBe(1000);
  });

  it("never scrolls below zero", () => {
    expect(autoscrollStep(10, -60, 1000, 1000)).toBe(0);
  });

  it("treats a negative max as zero", () => {
    expect(autoscrollStep(0, 60, 1000, -50)).toBe(0);
  });
});

describe("autoscrollAtEnd", () => {
  it("is true within a pixel of the bottom", () => {
    expect(autoscrollAtEnd(1000, 1000)).toBe(true);
    expect(autoscrollAtEnd(999.5, 1000)).toBe(true);
  });

  it("is false while scrolling remains", () => {
    expect(autoscrollAtEnd(500, 1000)).toBe(false);
  });
});

describe("clampAutoscrollSpeed", () => {
  it("clamps to the configured range", () => {
    expect(clampAutoscrollSpeed(0)).toBe(AUTOSCROLL_MIN_SPEED);
    expect(clampAutoscrollSpeed(9999)).toBe(AUTOSCROLL_MAX_SPEED);
    expect(clampAutoscrollSpeed(60)).toBe(60);
  });

  it("falls back to the default for NaN", () => {
    expect(clampAutoscrollSpeed(Number.NaN)).toBe(AUTOSCROLL_DEFAULT_SPEED);
  });
});

describe("clampFontSize", () => {
  it("clamps to the readable range", () => {
    expect(clampFontSize(4)).toBe(16);
    expect(clampFontSize(999)).toBe(48);
    expect(clampFontSize(24)).toBe(24);
  });
});
