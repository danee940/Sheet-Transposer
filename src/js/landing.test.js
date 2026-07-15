import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const initCapo = vi.fn();
const initPaste = vi.fn();
const initSyncedPanes = vi.fn();

vi.mock("./capo.js", () => ({ initCapo }));
vi.mock("./paste.js", () => ({ initPaste }));
vi.mock("./panes.js", () => ({ initSyncedPanes }));

describe("landing entry point", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("initialises nothing when the landing widgets are absent", async () => {
    await import("./landing.js");
    expect(initPaste).not.toHaveBeenCalled();
    expect(initSyncedPanes).not.toHaveBeenCalled();
    expect(initCapo).not.toHaveBeenCalled();
  });

  it("initialises the paste panel and capo table when present", async () => {
    document.body.innerHTML = `<div id="panel-paste"></div><div id="capo-key"></div>`;
    await import("./landing.js");
    expect(initPaste).toHaveBeenCalledOnce();
    expect(initSyncedPanes).toHaveBeenCalledOnce();
    expect(initCapo).toHaveBeenCalledOnce();
  });
});
