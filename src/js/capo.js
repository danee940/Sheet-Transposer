import { makeCell, makeHeaderCell } from "./dom.js";

export function initCapo() {
  const capoKey = document.getElementById("capo-key");
  const capoTableOutput = document.getElementById("capo-table-output");

  const CAPO_NOTE_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
  const CAPO_FRIENDLY_SHAPES = [
    { semitone: 0, major: "C", minor: "Am" },
    { semitone: 2, major: "D", minor: "Bm" },
    { semitone: 4, major: "E", minor: "C#m" },
    { semitone: 5, major: "F", minor: "Dm" },
    { semitone: 7, major: "G", minor: "Em" },
    { semitone: 9, major: "A", minor: "F#m" },
  ];
  const MAX_CAPO_FRET = 7;

  function keyToCapoSemitone(key) {
    const cleaned = key.replace(/m$/, "");
    return CAPO_NOTE_NAMES.reduce((acc, name, index) => {
      if (acc !== null) return acc;
      const sharpName = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][index];
      return name === cleaned || sharpName === cleaned ? index : null;
    }, null);
  }

  function renderCapoTable() {
    const key = capoKey.value;
    const isMinor = key.endsWith("m");
    const tonic = keyToCapoSemitone(key);
    capoTableOutput.replaceChildren();
    if (tonic === null) return;

    const rows = [];
    for (const shape of CAPO_FRIENDLY_SHAPES) {
      const fret = (tonic - shape.semitone + 12) % 12;
      if (fret > MAX_CAPO_FRET) continue;
      rows.push({ fret, shape: isMinor ? shape.minor : shape.major });
    }
    rows.sort((a, b) => a.fret - b.fret);

    const table = document.createElement("table");
    table.className = "w-full border-collapse";
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    headRow.className = "text-left text-muted-light dark:text-muted";
    headRow.appendChild(makeHeaderCell("Capo fret", "pb-2 pr-4 font-medium"));
    headRow.appendChild(makeHeaderCell("Play shape", "pb-2 pr-4 font-medium"));
    headRow.appendChild(makeHeaderCell("Sounds like", "pb-2 font-medium"));
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const row of rows) {
      const tr = document.createElement("tr");
      tr.className = "border-t border-app-border-light dark:border-app-border";
      tr.appendChild(makeCell(row.fret === 0 ? "No capo" : String(row.fret), "py-2 pr-4"));
      tr.appendChild(makeCell(row.shape, "py-2 pr-4 font-mono text-slate-900 dark:text-slate-100"));
      tr.appendChild(makeCell(key, "py-2 font-mono text-slate-900 dark:text-slate-100"));
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    capoTableOutput.appendChild(table);
  }

  capoKey.addEventListener("change", renderCapoTable);
  renderCapoTable();
}
