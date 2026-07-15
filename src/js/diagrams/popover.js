import { renderDiagram } from "./render.js";

export function createChordPopover(getInstrument) {
  let element = null;
  let content = null;
  let anchor = null;

  function ensureElement() {
    if (element !== null) return;
    element = document.createElement("div");
    element.className =
      "chord-popover absolute z-50 hidden w-max max-w-xs rounded-xl border border-app-border-light bg-card-light p-3 shadow-lg dark:border-app-border dark:bg-card";
    element.setAttribute("role", "dialog");
    element.setAttribute("aria-label", "Chord fingering");

    const close = document.createElement("button");
    close.type = "button";
    close.className =
      "chord-popover-close absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-md text-muted-light transition-colors hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-accent dark:text-muted dark:hover:text-slate-100";
    close.setAttribute("aria-label", "Close chord diagram");
    close.textContent = "×";
    close.addEventListener("click", () => hide());

    content = document.createElement("div");
    content.className = "chord-popover-content mt-2";

    element.appendChild(close);
    element.appendChild(content);
    document.body.appendChild(element);
  }

  function position() {
    const rect = anchor.getBoundingClientRect();
    const popRect = element.getBoundingClientRect();
    let left = window.scrollX + rect.left + rect.width / 2 - popRect.width / 2;
    left = Math.max(window.scrollX + 8, Math.min(left, window.scrollX + window.innerWidth - popRect.width - 8));
    let top = window.scrollY + rect.bottom + 8;
    if (rect.bottom + popRect.height + 8 > window.innerHeight) {
      top = window.scrollY + rect.top - popRect.height - 8;
    }
    element.style.left = `${Math.round(left)}px`;
    element.style.top = `${Math.round(top)}px`;
  }

  function onKeydown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      hide();
    }
  }

  function onPointerdown(event) {
    if (element.contains(event.target) || event.target === anchor) return;
    hide();
  }

  function hide() {
    if (element === null || element.classList.contains("hidden")) return;
    element.classList.add("hidden");
    document.removeEventListener("keydown", onKeydown, true);
    document.removeEventListener("pointerdown", onPointerdown, true);
    const previous = anchor;
    anchor = null;
    if (previous) previous.focus();
  }

  function show(triggerElement, chord) {
    ensureElement();
    anchor = triggerElement;
    content.replaceChildren(renderDiagram(chord, getInstrument()));
    element.classList.remove("hidden");
    position();
    document.addEventListener("keydown", onKeydown, true);
    document.addEventListener("pointerdown", onPointerdown, true);
    const close = element.querySelector(".chord-popover-close");
    if (close) close.focus();
  }

  return { show, hide };
}
