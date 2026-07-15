import { afterEach, describe, expect, it, vi } from "vitest";

const initUpload = vi.fn();
const initTabs = vi.fn();
const initPaste = vi.fn();
const initCapo = vi.fn();
const initSyncedPanes = vi.fn();

vi.mock("./upload.js", () => ({ initUpload }));
vi.mock("./tabs.js", () => ({ initTabs }));
vi.mock("./paste.js", () => ({ initPaste }));
vi.mock("./capo.js", () => ({ initCapo }));
vi.mock("./panes.js", () => ({ initSyncedPanes }));

describe("main entry point", () => {
  afterEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it("wires up every feature on load", async () => {
    await import("./main.js");
    expect(initUpload).toHaveBeenCalledOnce();
    expect(initTabs).toHaveBeenCalledOnce();
    expect(initPaste).toHaveBeenCalledOnce();
    expect(initCapo).toHaveBeenCalledOnce();
    expect(initSyncedPanes).toHaveBeenCalledOnce();
  });
});
