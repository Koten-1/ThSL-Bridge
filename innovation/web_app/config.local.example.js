// Local-only Typhoon API key for testing sentence-forming in the browser.
//
// Copy this file to config.local.js (same folder) and fill in your real key:
//   cp config.local.example.js config.local.js
// then edit config.local.js to replace the placeholder below.
//
// config.local.js is gitignored -- it will never be committed. If it's missing
// entirely, the page still works fine, it just falls back to showing the raw
// signed words instead of a Typhoon-formed sentence (same graceful-degradation
// behavior as the desktop pipeline's postprocess.py).
//
// SECURITY NOTE: this embeds the key in client-side JS, readable by anyone who
// opens dev tools. Fine for local testing on your own machine. Do NOT use this
// pattern if this page is ever deployed publicly (e.g. GitHub Pages) -- that
// would expose the key to every visitor. A public deployment would need a
// backend proxy instead.

window.TYPHOON_API_KEY = "your-typhoon-api-key-here";
