import { ACTIVE_TAB_CLASSES, INACTIVE_TAB_CLASSES } from "./dom.js";

export function initTabs() {
  const tabPaste = document.getElementById("tab-paste");
  const tabUpload = document.getElementById("tab-upload");
  const panelPaste = document.getElementById("panel-paste");
  const panelUpload = document.getElementById("panel-upload");

  function selectTab(active) {
    const paste = active === "paste";
    tabPaste.setAttribute("aria-selected", String(paste));
    tabUpload.setAttribute("aria-selected", String(!paste));
    panelPaste.classList.toggle("hidden", !paste);
    panelUpload.classList.toggle("hidden", paste);
    tabPaste.classList.remove(...ACTIVE_TAB_CLASSES, ...INACTIVE_TAB_CLASSES);
    tabUpload.classList.remove(...ACTIVE_TAB_CLASSES, ...INACTIVE_TAB_CLASSES);
    tabPaste.classList.add(...(paste ? ACTIVE_TAB_CLASSES : INACTIVE_TAB_CLASSES));
    tabUpload.classList.add(...(paste ? INACTIVE_TAB_CLASSES : ACTIVE_TAB_CLASSES));
  }

  tabPaste.addEventListener("click", () => selectTab("paste"));
  tabUpload.addEventListener("click", () => selectTab("upload"));
  selectTab("paste");
}
