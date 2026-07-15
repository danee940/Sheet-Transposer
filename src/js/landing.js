import { initCapo } from "./capo.js";
import { initSyncedPanes } from "./panes.js";
import { initPaste } from "./paste.js";
import { initUpload } from "./upload.js";

if (document.getElementById("panel-paste")) {
  initPaste();
  initSyncedPanes();
}
if (document.getElementById("form")) initUpload();
if (document.getElementById("capo-key")) initCapo();
