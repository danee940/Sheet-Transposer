import { initCapo } from "./capo.js";
import { initSyncedPanes } from "./panes.js";
import { initPaste } from "./paste.js";
import { initTabs } from "./tabs.js";
import { initUpload } from "./upload.js";

initUpload();
initTabs();
initPaste();
if (document.getElementById("capo-key")) initCapo();
initSyncedPanes();
