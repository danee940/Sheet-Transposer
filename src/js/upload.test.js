import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { initUpload } from "./upload.js";

function setupDom() {
  document.body.innerHTML = `
    <form id="form">
      <input id="file" type="file" name="file" />
      <div id="dropzone"><span id="dropzone-text"></span></div>
      <select id="current_key"><option value="C">C</option><option value="D">D</option></select>
      <select id="target_key"><option value="C">C</option><option value="D">D</option></select>
      <button id="swap" type="button"></button>
      <label><input type="radio" name="format" value="docx" checked /></label>
      <label><input type="radio" name="format" value="pdf" /></label>
      <button id="submit" type="submit"><span id="submit-label"></span><span id="spinner"></span></button>
      <div id="message"></div>
    </form>
  `;
}

function makeFile(name, size) {
  const file = new File(["x".repeat(Math.max(size, 0))], name);
  Object.defineProperty(file, "size", { value: size });
  return file;
}

function setFiles(input, files) {
  Object.defineProperty(input, "files", { value: files, configurable: true });
}

function response(overrides = {}) {
  return {
    ok: true,
    headers: {
      get: (name) =>
        ({
          "X-Transpose-From": "C",
          "X-Transpose-To": "D",
          "X-Transpose-Changes": "C->D, G->A",
          "Content-Disposition": 'attachment; filename="song.docx"',
          ...overrides.headers,
        })[name] ?? null,
    },
    json: async () => overrides.json ?? {},
    blob: async () => new Blob(["data"]),
    ...overrides.top,
  };
}

describe("initUpload", () => {
  let clickSpy;

  beforeEach(() => {
    setupDom();
    vi.stubGlobal("fetch", vi.fn());
    globalThis.URL.createObjectURL = vi.fn(() => "blob:mock");
    globalThis.URL.revokeObjectURL = vi.fn();
    globalThis.DataTransfer = class {
      constructor() {
        this._files = [];
        this.items = { add: (file) => this._files.push(file) };
      }
      get files() {
        return this._files;
      }
    };
    clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  function message() {
    return document.getElementById("message");
  }

  it("validates the file on change and shows the file summary", () => {
    initUpload();
    const fileInput = document.getElementById("file");
    setFiles(fileInput, [makeFile("song.docx", 2048)]);
    fileInput.dispatchEvent(new Event("change"));
    expect(document.getElementById("dropzone-text").textContent).toContain("song.docx");
  });

  it("formats small files in KB and rejects wrong extensions", () => {
    initUpload();
    const fileInput = document.getElementById("file");
    setFiles(fileInput, [makeFile("song.txt", 500)]);
    fileInput.dispatchEvent(new Event("change"));
    expect(message().textContent).toBe("Only .docx files are supported.");
    expect(document.getElementById("dropzone-text").innerHTML).toContain("Drop your .docx");
  });

  it("shows MB sizing for larger files", () => {
    initUpload();
    const fileInput = document.getElementById("file");
    setFiles(fileInput, [makeFile("big.docx", 3 * 1024 * 1024)]);
    fileInput.dispatchEvent(new Event("change"));
    expect(document.getElementById("dropzone-text").textContent).toContain("3.0 MB");
  });

  it("rejects empty and oversized files", () => {
    initUpload();
    const fileInput = document.getElementById("file");
    setFiles(fileInput, [makeFile("empty.docx", 0)]);
    fileInput.dispatchEvent(new Event("change"));
    expect(message().textContent).toBe("The selected file is empty.");

    setFiles(fileInput, [makeFile("huge.docx", 11 * 1024 * 1024)]);
    fileInput.dispatchEvent(new Event("change"));
    expect(message().textContent).toBe("File is too large. The maximum size is 10 MB.");
  });

  it("toggles the dropzone drag styling", () => {
    initUpload();
    const dropzone = document.getElementById("dropzone");
    dropzone.dispatchEvent(new Event("dragenter"));
    expect(dropzone.classList.contains("border-accent")).toBe(true);
    dropzone.dispatchEvent(new Event("dragleave"));
    expect(dropzone.classList.contains("border-accent")).toBe(false);
  });

  it("accepts a dropped file", () => {
    initUpload();
    const fileInput = document.getElementById("file");
    let assigned = [];
    Object.defineProperty(fileInput, "files", {
      configurable: true,
      get: () => assigned,
      set: (value) => {
        assigned = value;
      },
    });
    const dropzone = document.getElementById("dropzone");
    const event = new Event("drop");
    event.dataTransfer = { files: [makeFile("dropped.docx", 1024)] };
    dropzone.dispatchEvent(event);
    expect(document.getElementById("dropzone-text").textContent).toContain("dropped.docx");
  });

  it("ignores a drop with no file", () => {
    initUpload();
    const dropzone = document.getElementById("dropzone");
    const event = new Event("drop");
    event.dataTransfer = { files: [] };
    dropzone.dispatchEvent(event);
    expect(document.getElementById("dropzone-text").textContent).toBe("");
  });

  it("swaps the current and target keys", () => {
    initUpload();
    document.getElementById("current_key").value = "C";
    document.getElementById("target_key").value = "D";
    document.getElementById("swap").dispatchEvent(new Event("click"));
    expect(document.getElementById("current_key").value).toBe("D");
    expect(document.getElementById("target_key").value).toBe("C");
  });

  it("blocks submission without a valid file", async () => {
    initUpload();
    const fileInput = document.getElementById("file");
    setFiles(fileInput, []);
    document.getElementById("form").dispatchEvent(new Event("submit"));
    await Promise.resolve();
    expect(message().textContent).toBe("Please choose a .docx file to upload.");
    expect(fetch).not.toHaveBeenCalled();
  });

  it("blocks submission when the keys match", async () => {
    initUpload();
    setFiles(document.getElementById("file"), [makeFile("song.docx", 1024)]);
    document.getElementById("current_key").value = "C";
    document.getElementById("target_key").value = "C";
    document.getElementById("form").dispatchEvent(new Event("submit"));
    await Promise.resolve();
    expect(message().textContent).toContain("same");
  });

  async function submitValid() {
    setFiles(document.getElementById("file"), [makeFile("song.docx", 1024)]);
    document.getElementById("current_key").value = "C";
    document.getElementById("target_key").value = "D";
    document.getElementById("form").dispatchEvent(new Event("submit"));
    await vi.waitFor(() => expect(document.getElementById("spinner").classList.contains("hidden")).toBe(true));
  }

  it("downloads the file and renders the change table on success", async () => {
    fetch.mockResolvedValue(response());
    initUpload();
    await submitValid();
    expect(clickSpy).toHaveBeenCalled();
    expect(message().textContent).toContain("Transposed from C to D");
    expect(message().querySelectorAll("tbody tr")).toHaveLength(2);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock");
  });

  it("shows the server error message on a non-ok response", async () => {
    fetch.mockResolvedValue(
      response({ top: { ok: false }, json: { error: "Bad key." } })
    );
    initUpload();
    await submitValid();
    expect(message().textContent).toBe("Bad key.");
  });

  it("falls back to a generic error when the body is not JSON", async () => {
    fetch.mockResolvedValue({
      ok: false,
      headers: { get: () => null },
      json: () => Promise.reject(new Error("nope")),
    });
    initUpload();
    await submitValid();
    expect(message().textContent).toBe("Something went wrong.");
  });

  it("uses a generic error when the JSON omits an error field", async () => {
    fetch.mockResolvedValue(response({ top: { ok: false }, json: {} }));
    initUpload();
    await submitValid();
    expect(message().textContent).toBe("Something went wrong.");
  });

  it("reports a network error when fetch rejects", async () => {
    fetch.mockRejectedValue(new Error("offline"));
    initUpload();
    await submitValid();
    expect(message().textContent).toBe("Network error. Please try again.");
  });

  it("parses an extended UTF-8 filename", async () => {
    fetch.mockResolvedValue(
      response({ headers: { "Content-Disposition": "attachment; filename*=UTF-8''caf%C3%A9.docx" } })
    );
    initUpload();
    const anchorSpy = vi.spyOn(document, "createElement");
    await submitValid();
    const anchor = anchorSpy.mock.results.map((r) => r.value).find((el) => el.tagName === "A");
    expect(anchor.download).toBe("café.docx");
  });

  it("falls back when the extended filename cannot be decoded", async () => {
    fetch.mockResolvedValue(
      response({ headers: { "Content-Disposition": "attachment; filename*=UTF-8''%E0%A4%A.docx" } })
    );
    initUpload();
    const anchorSpy = vi.spyOn(document, "createElement");
    await submitValid();
    const anchor = anchorSpy.mock.results.map((r) => r.value).find((el) => el.tagName === "A");
    expect(anchor.download).toBe("transposed.docx");
  });

  it("parses a bare filename and default header values", async () => {
    fetch.mockResolvedValue(
      response({
        headers: {
          "Content-Disposition": "attachment; filename=plain.docx",
          "X-Transpose-From": null,
          "X-Transpose-To": null,
          "X-Transpose-Changes": null,
        },
      })
    );
    initUpload();
    const anchorSpy = vi.spyOn(document, "createElement");
    await submitValid();
    const anchor = anchorSpy.mock.results.map((r) => r.value).find((el) => el.tagName === "A");
    expect(anchor.download).toBe("plain.docx");
    expect(message().textContent).toContain("Transposed from ? to ?");
  });

  it("defaults to docx when no format radio is checked and no disposition", async () => {
    document.querySelector('input[value="docx"]').checked = false;
    fetch.mockResolvedValue(response({ headers: { "Content-Disposition": null } }));
    initUpload();
    const anchorSpy = vi.spyOn(document, "createElement");
    await submitValid();
    const anchor = anchorSpy.mock.results.map((r) => r.value).find((el) => el.tagName === "A");
    expect(anchor.download).toBe("transposed.docx");
  });

  it("falls back to the selected format when no disposition is present", async () => {
    document.querySelector('input[value="pdf"]').checked = true;
    document.querySelector('input[value="docx"]').checked = false;
    fetch.mockResolvedValue(response({ headers: { "Content-Disposition": null } }));
    initUpload();
    const anchorSpy = vi.spyOn(document, "createElement");
    await submitValid();
    const anchor = anchorSpy.mock.results.map((r) => r.value).find((el) => el.tagName === "A");
    expect(anchor.download).toBe("transposed.pdf");
  });
});
