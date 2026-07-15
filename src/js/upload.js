import { BASE_CLASSES, ERROR_CLASSES, OK_CLASSES, makeCell, makeHeaderCell } from "./dom.js";

export function initUpload() {
  const form = document.getElementById("form");
  const submit = document.getElementById("submit");
  const submitLabel = document.getElementById("submit-label");
  const spinner = document.getElementById("spinner");
  const message = document.getElementById("message");
  const fileInput = document.getElementById("file");
  const dropzone = document.getElementById("dropzone");
  const dropzoneText = document.getElementById("dropzone-text");
  const currentKey = document.getElementById("current_key");
  const targetKey = document.getElementById("target_key");
  const swap = document.getElementById("swap");

  const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
  const DEFAULT_DROPZONE_HTML =
    '<span class="font-medium text-slate-800 dark:text-slate-200">Drop your .docx here</span> or click to browse';

  function hideMessage() {
    message.className = BASE_CLASSES + " hidden";
    message.replaceChildren();
  }

  function show(kind, text) {
    message.className = BASE_CLASSES + " " + (kind === "error" ? ERROR_CLASSES : OK_CLASSES);
    message.textContent = text;
  }

  function formatBytes(bytes) {
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? `${mb.toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }

  function validateFile(file) {
    if (!file) return "Please choose a .docx file to upload.";
    if (!file.name.toLowerCase().endsWith(".docx")) return "Only .docx files are supported.";
    if (file.size === 0) return "The selected file is empty.";
    if (file.size > MAX_UPLOAD_BYTES) return "File is too large. The maximum size is 10 MB.";
    return null;
  }

  function updateDropzone(file) {
    if (!file) {
      dropzoneText.innerHTML = DEFAULT_DROPZONE_HTML;
      return;
    }
    dropzoneText.innerHTML =
      `<span class="font-medium text-slate-800 dark:text-slate-200"></span>` +
      `<span class="block text-xs text-muted-light dark:text-muted"></span>`;
    dropzoneText.firstChild.textContent = file.name;
    dropzoneText.lastChild.textContent = formatBytes(file.size);
  }

  fileInput.addEventListener("change", () => {
    hideMessage();
    const file = fileInput.files[0];
    updateDropzone(file);
    const error = validateFile(file);
    if (file && error) {
      show("error", error);
      fileInput.value = "";
      updateDropzone(null);
    }
  });

  ["dragenter", "dragover"].forEach((name) =>
    dropzone.addEventListener(name, (event) => {
      event.preventDefault();
      dropzone.classList.add("border-accent", "bg-accent/5");
    })
  );
  ["dragleave", "dragend", "drop"].forEach((name) =>
    dropzone.addEventListener(name, (event) => {
      event.preventDefault();
      dropzone.classList.remove("border-accent", "bg-accent/5");
    })
  );
  dropzone.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (!file) return;
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
    fileInput.dispatchEvent(new Event("change"));
  });

  swap.addEventListener("click", () => {
    const from = currentKey.value;
    currentKey.value = targetKey.value;
    targetKey.value = from;
  });

  function showTransposeResult(from, to, changesRaw) {
    message.className = BASE_CLASSES + " " + OK_CLASSES;
    message.replaceChildren();

    const heading = document.createElement("div");
    heading.className = "mb-2 font-semibold";
    heading.textContent = `Transposed from ${from} to ${to}`;
    message.appendChild(heading);

    const pairs = changesRaw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s) => s.split("->"));

    const table = document.createElement("table");
    table.className = "w-full border-collapse";

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    headRow.className = "text-left opacity-60";
    headRow.appendChild(makeHeaderCell("Before", "pb-1 pr-4 font-medium"));
    headRow.appendChild(makeHeaderCell("After", "pb-1 font-medium"));
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const [orig, transposed] of pairs) {
      const row = document.createElement("tr");
      row.className = "border-t border-app-ok/20";
      row.appendChild(makeCell(orig, "py-1 pr-4 font-mono"));
      row.appendChild(makeCell(transposed, "py-1 font-mono"));
      tbody.appendChild(row);
    }
    table.appendChild(tbody);

    message.appendChild(table);
  }

  function parseDownloadFilename(disposition, fallback) {
    const extendedMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (extendedMatch) {
      try {
        return decodeURIComponent(extendedMatch[1]);
      } catch {
        return fallback;
      }
    }
    const quotedMatch = disposition.match(/filename="([^"]+)"/i);
    if (quotedMatch) {
      return quotedMatch[1];
    }
    const bareMatch = disposition.match(/filename=([^;]+)/i);
    if (bareMatch) {
      return bareMatch[1].trim();
    }
    return fallback;
  }

  function setLoading(loading) {
    submit.disabled = loading;
    spinner.classList.toggle("hidden", !loading);
    submitLabel.textContent = loading ? "Transposing..." : "Transpose & Download";
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideMessage();

    const fileError = validateFile(fileInput.files[0]);
    if (fileError) {
      show("error", fileError);
      return;
    }
    if (currentKey.value === targetKey.value) {
      show("error", "Current and desired keys are the same. Pick a different key to transpose.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/transpose", { method: "POST", body: new FormData(form) });

      if (!response.ok) {
        const data = await response.json().catch(() => ({ error: "Something went wrong." }));
        show("error", data.error || "Something went wrong.");
        return;
      }

      const from = decodeURIComponent(response.headers.get("X-Transpose-From") || "?");
      const to = decodeURIComponent(response.headers.get("X-Transpose-To") || "?");
      const changes = decodeURIComponent(response.headers.get("X-Transpose-Changes") || "none");

      const disposition = response.headers.get("Content-Disposition") || "";
      const selectedFormat = form.querySelector('input[name="format"]:checked')?.value || "docx";
      const filename = parseDownloadFilename(disposition, `transposed.${selectedFormat}`);

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);

      showTransposeResult(from, to, changes);
    } catch (err) {
      show("error", "Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  });
}
