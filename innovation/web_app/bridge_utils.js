// Small pure helpers for the bridge UI: no DOM, no network, so they can be tested on their own.
// Plain script (no import/export) so it works from a double-clicked page. Global: BridgeUtils.
//
//   createLookup(words)      Thai text -> which words are in the 33-word vocabulary, which are not
//   pickThaiVoice(voices)    choose a Thai text-to-speech voice, and say whether it sends text off the device
(function (root) {
  function normalize(text) {
    return String(text == null ? "" : text).replace(/[​-‍﻿]/g, "").replace(/\s+/g, " ").trim();
  }

  function makeSegmenter() {
    try { if (typeof Intl !== "undefined" && Intl.Segmenter) return new Intl.Segmenter("th", { granularity: "word" }); } catch (e) { /* fall back */ }
    return null;
  }

  // words: [{ th, ... }]. opts.segmenter: pass null to force the fallback (used by tests).
  function createLookup(words, opts) {
    const o = Object.assign({ segmenter: undefined }, opts || {});
    const seg = o.segmenter === undefined ? makeSegmenter() : o.segmenter;
    const byText = new Map(words.map(w => [w.th, w]));
    const longestFirst = words.map(w => w.th).sort((a, b) => b.length - a.length);

    // Fallback when the browser has no Thai word segmenter: longest vocabulary match from the left,
    // text between matches stays "unsupported". Less accurate (it can match inside a longer word).
    function greedy(chunk) {
      const items = []; let i = 0, pending = "";
      while (i < chunk.length) {
        const hit = longestFirst.find(t => chunk.startsWith(t, i));
        if (hit) {
          if (pending) { items.push({ text: pending, supported: false }); pending = ""; }
          items.push({ text: hit, supported: true, word: byText.get(hit) });
          i += hit.length;
        } else { pending += chunk[i]; i++; }
      }
      if (pending) items.push({ text: pending, supported: false });
      return items;
    }

    function lookup(text) {
      const t = normalize(text);
      let items = [];
      if (t) {
        if (seg) {
          for (const s of seg.segment(t)) {
            const piece = s.segment;
            if (!piece.trim()) continue;
            if (s.isWordLike === false && !/[฀-๿]/.test(piece)) continue;      // punctuation and symbols
            const w = byText.get(piece);
            items.push(w ? { text: piece, supported: true, word: w } : { text: piece, supported: false });
          }
        } else {
          for (const chunk of t.split(/[\s,.;:!?()"'\-]+/)) if (chunk) items = items.concat(greedy(chunk));
        }
      }
      // neighbouring unsupported pieces are one phrase for the reader (Thai has no spaces)
      const merged = [];
      for (const it of items) {
        const last = merged[merged.length - 1];
        if (!it.supported && last && !last.supported) last.text += it.text; else merged.push(Object.assign({}, it));
      }
      return {
        items: merged,
        supported: merged.filter(x => x.supported).map(x => x.word),
        unsupported: merged.filter(x => !x.supported).map(x => x.text),
      };
    }
    return { lookup, has: th => byText.has(th), size: words.length, usesSegmenter: !!seg };
  }

  // voices: speechSynthesis.getVoices(). A voice with localService=true runs on the device, so no text leaves it.
  // A remote voice (for example Chrome's Google Thai voice) sends the text to a server, so it needs allowRemote.
  function pickThaiVoice(voices, allowRemote) {
    const th = (voices || []).filter(v => /^th([-_]|$)/i.test(v.lang || ""));
    const local = th.find(v => v.localService);
    if (local) return { voice: local, remote: false, reason: "local" };
    if (th.length && allowRemote) return { voice: th[0], remote: true, reason: "remote-allowed" };
    return { voice: null, remote: false, reason: th.length ? "remote-only" : "none" };
  }

  root.BridgeUtils = { normalize, createLookup, pickThaiVoice };
})(typeof window !== "undefined" ? window : globalThis);
