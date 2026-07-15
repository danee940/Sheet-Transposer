import { buildInteractiveOutput } from "./output.js";
import { createChordPopover } from "./popover.js";
import { parseChordSymbol } from "./shapes.js";

export function initDiagrams(getInstrument) {
  const popover = createChordPopover(getInstrument);

  function activate(button) {
    const chord = parseChordSymbol(button.dataset.chord, button.dataset.german === "1");
    popover.show(button, chord);
  }

  function renderInto(container, text) {
    popover.hide();
    container.replaceChildren(buildInteractiveOutput(text, activate));
  }

  return { renderInto, closePopover: popover.hide };
}
