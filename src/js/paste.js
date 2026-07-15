import { MODE_ACTIVE_CLASSES, MODE_INACTIVE_CLASSES } from "./dom.js";

export function initPaste() {
  const textInput = document.getElementById("text_input");
  const textOutput = document.getElementById("text_output");
  const textStatus = document.getElementById("text_status");
  const textCopy = document.getElementById("text_copy");
  const textCurrentKey = document.getElementById("text_current_key");
  const textTargetKey = document.getElementById("text_target_key");
  const textSwap = document.getElementById("text_swap");
  const textLineCount = document.getElementById("text_linecount");
  const textSample = document.getElementById("text_sample");
  const textClear = document.getElementById("text_clear");

  const modeKey = document.getElementById("mode-key");
  const modeSemitone = document.getElementById("mode-semitone");
  const modeNashville = document.getElementById("mode-nashville");
  const controlsKey = document.getElementById("controls-key");
  const controlsSemitone = document.getElementById("controls-semitone");
  const textCurrentKeyLabel = document.querySelector('label[for="text_current_key"]');
  const chordproFormatToggle = document.getElementById("chordpro-format-toggle");
  const formatChordpro = document.getElementById("format_chordpro");
  const formatPlain = document.getElementById("format_plain");
  const semitoneValue = document.getElementById("semitone_value");
  const semitoneDown = document.getElementById("semitone_down");
  const semitoneUp = document.getElementById("semitone_up");
  const semitoneQuick = document.querySelectorAll(".semitone-quick");
  const notationSharp = document.getElementById("notation_sharp");
  const notationFlat = document.getElementById("notation_flat");

  const panelPaste = document.getElementById("panel-paste");
  const MAX_SEMITONES = parseInt(panelPaste.dataset.maxSemitones, 10);
  const SAMPLE_CHORDS =
    "C           G           Am          F\n" +
    "Twinkle twinkle little star\n\n" +
    "C           G           C\n" +
    "How I wonder what you are\n\n" +
    "F      C      G      C\n" +
    "Up above the world so high";

  let transposeMode = "key";
  let semitones = 0;
  let useFlats = false;
  let outputFormat = "chordpro";
  let transposeTimer = null;
  let requestToken = 0;

  function setTextStatus(text) {
    textStatus.textContent = text;
  }

  function updateLineCount() {
    const value = textInput.value;
    const lines = value === "" ? 0 : value.split("\n").length;
    textLineCount.textContent = `${lines} line${lines === 1 ? "" : "s"}`;
  }

  function setModeButtonState(button, active) {
    button.setAttribute("aria-selected", String(active));
    button.classList.remove(...MODE_ACTIVE_CLASSES, ...MODE_INACTIVE_CLASSES);
    button.classList.add(...(active ? MODE_ACTIVE_CLASSES : MODE_INACTIVE_CLASSES));
  }

  function selectMode(mode) {
    transposeMode = mode;
    const key = mode === "key";
    const nashville = mode === "nashville";
    const showKeyControls = key || nashville;

    controlsKey.classList.toggle("hidden", !showKeyControls);
    controlsSemitone.classList.toggle("hidden", mode !== "semitone");

    textTargetKey.parentElement.classList.toggle("hidden", nashville);
    textSwap.classList.toggle("hidden", nashville);
    textCurrentKeyLabel.textContent = nashville ? "Tonic key" : "Current key";

    setModeButtonState(modeKey, key);
    setModeButtonState(modeSemitone, mode === "semitone");
    setModeButtonState(modeNashville, nashville);

    if (nashville) {
      chordproFormatToggle.classList.add("hidden");
    }
    runTextTranspose();
  }

  function updateSemitoneDisplay() {
    semitoneValue.textContent = semitones > 0 ? `+${semitones}` : String(semitones);
  }

  function setSemitones(value) {
    semitones = Math.max(-MAX_SEMITONES, Math.min(MAX_SEMITONES, value));
    updateSemitoneDisplay();
    runTextTranspose();
  }

  function selectNotation(flat) {
    useFlats = flat;
    notationSharp.setAttribute("aria-pressed", String(!flat));
    notationFlat.setAttribute("aria-pressed", String(flat));
    notationSharp.classList.remove(...MODE_ACTIVE_CLASSES, ...MODE_INACTIVE_CLASSES);
    notationFlat.classList.remove(...MODE_ACTIVE_CLASSES, ...MODE_INACTIVE_CLASSES);
    notationSharp.classList.add(...(flat ? MODE_INACTIVE_CLASSES : MODE_ACTIVE_CLASSES));
    notationFlat.classList.add(...(flat ? MODE_ACTIVE_CLASSES : MODE_INACTIVE_CLASSES));
    runTextTranspose();
  }

  function selectOutputFormat(plain) {
    outputFormat = plain ? "plain" : "chordpro";
    formatChordpro.setAttribute("aria-pressed", String(!plain));
    formatPlain.setAttribute("aria-pressed", String(plain));
    formatChordpro.classList.remove(...MODE_ACTIVE_CLASSES, ...MODE_INACTIVE_CLASSES);
    formatPlain.classList.remove(...MODE_ACTIVE_CLASSES, ...MODE_INACTIVE_CLASSES);
    formatChordpro.classList.add(...(plain ? MODE_INACTIVE_CLASSES : MODE_ACTIVE_CLASSES));
    formatPlain.classList.add(...(plain ? MODE_ACTIVE_CLASSES : MODE_INACTIVE_CLASSES));
    runTextTranspose();
  }

  function buildRequestBody(text) {
    if (transposeMode === "nashville") {
      return { text, tonic_key: textCurrentKey.value };
    }
    if (transposeMode === "semitone") {
      return { text, semitones, notation: useFlats ? "flat" : "sharp", output_format: outputFormat };
    }
    return {
      text,
      current_key: textCurrentKey.value,
      target_key: textTargetKey.value,
      output_format: outputFormat,
    };
  }

  function summariseResult(data) {
    if (transposeMode === "nashville") {
      return `Nashville · key of ${data.tonic}`;
    }
    const count = Array.isArray(data.changes) ? data.changes.length : 0;
    const label = transposeMode === "semitone" ? data.label : `${data.from} → ${data.to}`;
    return count > 0
      ? `${label} · ${count} chord${count === 1 ? "" : "s"} changed`
      : `${label} · no chords found to change`;
  }

  async function runTextTranspose() {
    const text = textInput.value;
    if (!text.trim()) {
      textOutput.textContent = "";
      textCopy.disabled = true;
      setTextStatus("");
      chordproFormatToggle.classList.add("hidden");
      return;
    }
    if (transposeMode === "key" && textCurrentKey.value === textTargetKey.value) {
      setTextStatus("Pick two different keys to transpose.");
      return;
    }
    if (transposeMode === "semitone" && semitones === 0) {
      textOutput.textContent = text;
      textCopy.disabled = !text;
      setTextStatus("No shift · pick a semitone offset to transpose.");
      return;
    }

    const token = ++requestToken;
    setTextStatus("Transposing…");

    const endpoint = transposeMode === "nashville" ? "/nashville-text" : "/transpose-text";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildRequestBody(text)),
      });
      if (token !== requestToken) return;

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        setTextStatus(data.error || "Something went wrong.");
        return;
      }

      const isChordPro = data.format === "chordpro" && transposeMode !== "nashville";
      chordproFormatToggle.classList.toggle("hidden", !isChordPro);

      textOutput.textContent = data.text;
      textCopy.disabled = !data.text;
      setTextStatus(summariseResult(data));
    } catch {
      if (token === requestToken) setTextStatus("Network error. Please try again.");
    }
  }

  function scheduleTextTranspose() {
    clearTimeout(transposeTimer);
    transposeTimer = setTimeout(runTextTranspose, 250);
  }

  textInput.addEventListener("input", () => {
    updateLineCount();
    scheduleTextTranspose();
  });
  textCurrentKey.addEventListener("change", runTextTranspose);
  textTargetKey.addEventListener("change", runTextTranspose);

  textSwap.addEventListener("click", () => {
    const from = textCurrentKey.value;
    textCurrentKey.value = textTargetKey.value;
    textTargetKey.value = from;
    runTextTranspose();
  });

  textSample.addEventListener("click", () => {
    textInput.value = SAMPLE_CHORDS;
    updateLineCount();
    runTextTranspose();
    textInput.focus();
  });

  textClear.addEventListener("click", () => {
    textInput.value = "";
    updateLineCount();
    runTextTranspose();
    textInput.focus();
  });

  modeKey.addEventListener("click", () => selectMode("key"));
  modeSemitone.addEventListener("click", () => selectMode("semitone"));
  modeNashville.addEventListener("click", () => selectMode("nashville"));
  formatChordpro.addEventListener("click", () => selectOutputFormat(false));
  formatPlain.addEventListener("click", () => selectOutputFormat(true));
  semitoneDown.addEventListener("click", () => setSemitones(semitones - 1));
  semitoneUp.addEventListener("click", () => setSemitones(semitones + 1));
  semitoneQuick.forEach((button) =>
    button.addEventListener("click", () => setSemitones(Number(button.dataset.semitone)))
  );
  notationSharp.addEventListener("click", () => selectNotation(false));
  notationFlat.addEventListener("click", () => selectNotation(true));

  document.addEventListener("keydown", (event) => {
    if (transposeMode !== "semitone") return;
    const target = event.target;
    const typing =
      target && (target.tagName === "TEXTAREA" || target.tagName === "INPUT" || target.tagName === "SELECT");
    if (typing) return;
    if (event.key === "[") {
      event.preventDefault();
      setSemitones(semitones - 1);
    } else if (event.key === "]") {
      event.preventDefault();
      setSemitones(semitones + 1);
    }
  });

  selectOutputFormat(false);
  selectMode("key");
  selectNotation(false);
  updateSemitoneDisplay();
  updateLineCount();

  textCopy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(textOutput.textContent);
      const original = textCopy.textContent;
      textCopy.textContent = "Copied";
      setTimeout(() => {
        textCopy.textContent = original;
      }, 1500);
    } catch {
      setTextStatus("Could not copy to clipboard.");
    }
  });
}
