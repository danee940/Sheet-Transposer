const PREFS_STORAGE_KEY = "chord-transposer:prefs";
const ALLOWED_PREF_KEYS = ["mode", "currentKey", "targetKey", "semitones", "notation", "instrument"];

export function sanitizePrefs(raw) {
  const clean = {};
  if (typeof raw !== "object" || raw === null) return clean;
  for (const key of ALLOWED_PREF_KEYS) {
    const value = raw[key];
    if (value === undefined || value === null) continue;
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      clean[key] = value;
    }
  }
  return clean;
}

export function loadPrefs() {
  try {
    const stored = localStorage.getItem(PREFS_STORAGE_KEY);
    if (!stored) return {};
    return sanitizePrefs(JSON.parse(stored));
  } catch {
    return {};
  }
}

export function savePrefs(prefs) {
  try {
    localStorage.setItem(PREFS_STORAGE_KEY, JSON.stringify(sanitizePrefs(prefs)));
  } catch {
    return;
  }
}
