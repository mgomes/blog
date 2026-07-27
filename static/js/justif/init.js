// Justify prose with justif after the MonoLisa webfonts are loaded.
// justif's auto.js measures at render-blocking time, before self-hosted
// fonts arrive, and ends up justifying against fallback-font metrics.
import { justify } from "/js/justif/index.js";
import { hyphenateEnUS } from "/js/justif/hyphenate/en-us.js";

const fonts = [
  "400 16px MonoLisaText",
  "italic 400 16px MonoLisaText",
  "600 16px MonoLisaText",
];

async function run() {
  fonts.forEach((f) => document.fonts.load(f));
  await document.fonts.ready;
  // Keep this selector in sync with the text-align: justify rule in main.css.
  const targets = document.querySelectorAll(
    ".container p:not(.light), .container li, .container blockquote"
  );
  // hangingPunctuation corrupts line measurement on this site (hyphens and
  // commas land at line starts, and paragraphs with links get huge word
  // gaps), so it stays off.
  justify(targets, { hyphenate: hyphenateEnUS, hangingPunctuation: false });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", run);
} else {
  run();
}
