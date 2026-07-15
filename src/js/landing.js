import { initCapo } from "./capo.js";
import { initSyncedPanes } from "./panes.js";
import { initPaste } from "./paste.js";

if (document.getElementById("panel-paste")) {
  initPaste();
  initSyncedPanes();
}
if (document.getElementById("capo-key")) initCapo();
