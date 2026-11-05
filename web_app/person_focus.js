// Person focus: when several people stand in front of the camera, use only the hands
// that belong to the user whose face is the main one.
//
// Pure geometry on numbers (no camera, no network), so it can be tested on its own.
// Plain script (no import/export) so a double-clicked page can load it. Global: PersonFocus.
//
// Coordinates are MediaPipe's normalized image coordinates (0..1). `aspect` is
// video width / height, used so that horizontal and vertical distances are comparable.
// Distances below are measured in "face widths" of the face being tested, which makes the
// rules independent of how far each person stands from the camera.
(function (root) {
  const DEFAULTS = {
    holdMs: 1500,        // keep the locked face this long after it disappears (a hand can cover it)
    switchRatio: 1.4,    // a different face must be this much bigger (area) to take over while the locked one is visible
    sameFaceDist: 1.0,   // a box is "the same person" if its centre moved less than this many face widths
    reachX: 2.6,         // wrist may be this many face widths left or right of the face centre
    reachUp: 1.5,        // ... above the top of the face
    reachDown: 4.5,      // ... below the chin
    minHandRatio: 0.15,  // wrist to middle-knuckle length / face width. Loose on purpose: a hand pointing at the camera looks short
    maxHandRatio: 2.2,
    maxHands: 2,
  };

  const area = b => b.w * b.h;

  function create(opts) {
    return { o: Object.assign({}, DEFAULTS, opts || {}), primary: null, faces: [], lastSeen: 0 };
  }

  function reset(st) { st.primary = null; st.faces = []; return st; }

  // boxes: [{x, y, w, h}] of the faces seen this frame. Picks and keeps the main face.
  function update(st, boxes, tMs, aspect) {
    aspect = aspect || 1;
    const o = st.o;
    st.faces = boxes.slice();
    if (!boxes.length) {
      if (st.primary && tMs - st.lastSeen > o.holdMs) st.primary = null;
      return st;
    }
    const largest = boxes.reduce((a, b) => (area(b) > area(a) ? b : a));
    if (!st.primary) { st.primary = largest; st.lastSeen = tMs; return st; }

    const pc = { x: st.primary.x + st.primary.w / 2, y: st.primary.y + st.primary.h / 2 };
    const fw = st.primary.w * aspect;
    let match = null, md = Infinity;
    for (const b of boxes) {
      const d = Math.hypot((b.x + b.w / 2 - pc.x) * aspect, b.y + b.h / 2 - pc.y) / fw;
      if (d < md) { md = d; match = b; }
    }
    if (match && md <= o.sameFaceDist) {
      // the locked person is still here; only a clearly closer (bigger) person takes over
      st.primary = area(largest) > area(match) * o.switchRatio ? largest : match;
      st.lastSeen = tMs;
    } else if (tMs - st.lastSeen > o.holdMs) {
      st.primary = largest; st.lastSeen = tMs;
    }
    // else: the locked face is not visible right now (for example a hand covers it): keep the old box
    return st;
  }

  // How well a hand fits a face's owner, as a distance (smaller = closer to that person's body).
  // null = the hand cannot belong to this face at all.
  function score(hand, f, aspect, o) {
    const fw = f.w * aspect;
    if (!(fw > 0)) return null;
    const cx = (f.x + f.w / 2) * aspect, top = f.y, bottom = f.y + f.h;
    const wx = hand[0].x * aspect, wy = hand[0].y;       // wrist
    const mx = hand[9].x * aspect, my = hand[9].y;       // middle-finger knuckle
    const ratio = Math.hypot(wx - mx, wy - my) / fw;
    if (ratio < o.minHandRatio || ratio > o.maxHandRatio) return null;
    if (Math.abs(wx - cx) / fw > o.reachX) return null;
    if ((top - wy) / fw > o.reachUp || (wy - bottom) / fw > o.reachDown) return null;
    const ay = bottom + 0.8 * f.h;                        // roughly the upper chest
    return Math.hypot((wx - cx) / fw, (wy - ay) / fw);
  }

  // hands: array of 21-point landmark arrays. Returns which ones belong to the locked user.
  function filterHands(st, hands, aspect) {
    aspect = aspect || 1;
    const n = hands.length;
    const keep = new Array(n).fill(true), owner = new Array(n).fill(-1), reason = new Array(n).fill("");
    if (!st.primary) {                                    // nobody to anchor to: do not block anything
      reason.fill("no-face");
      return { keep, owner, reason, filtered: false };
    }
    const faces = st.faces.slice();
    if (faces.indexOf(st.primary) < 0) faces.push(st.primary);   // the locked face may be held, not detected this frame
    const mineScore = new Array(n).fill(Infinity);
    for (let i = 0; i < n; i++) {
      let best = -1, bestScore = Infinity;
      for (let j = 0; j < faces.length; j++) {
        const s = score(hands[i], faces[j], aspect, st.o);
        if (s !== null && s < bestScore) { bestScore = s; best = j; }
      }
      owner[i] = best;
      const mine = best >= 0 && faces[best] === st.primary;
      keep[i] = mine;
      reason[i] = mine ? "user" : best < 0 ? "out-of-reach" : "other-person";
      if (mine) mineScore[i] = bestScore;
    }
    // one person has two hands at most: keep the two closest to their body
    const mineIdx = [];
    for (let i = 0; i < n; i++) if (keep[i]) mineIdx.push(i);
    mineIdx.sort((a, b) => mineScore[a] - mineScore[b]);
    mineIdx.slice(st.o.maxHands).forEach(i => { keep[i] = false; reason[i] = "extra"; });
    return { keep, owner, reason, filtered: true };
  }

  root.PersonFocus = { DEFAULTS, create, reset, update, filterHands, score };
})(typeof window !== "undefined" ? window : globalThis);
