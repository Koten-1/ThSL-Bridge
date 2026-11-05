// Where does one sign start and stop? The single rule shared by training and this web app.
//
// The same algorithm is in scripts/capture_rule.py, which cuts the training clips. Keep the two identical:
// training clips and live capture must be cut the same way. Plain script (no import/export), global: CaptureRule.
//
// A sign starts when the hand MOVES and ends when it has been STILL for a moment. Movement is how much the hand
// changed compared with 200 ms ago, not frame to frame: real signing changes only ~0.001 per frame, the same size as
// camera jitter, but over 200 ms the change is clearly larger than the jitter. Only coordinates present in both frames
// are compared, so a hand dropping out for one frame does not look like movement.
//
// A row is a (126) array, left hand 63 + right hand 63, zeros = hand absent, or null = no hand. Times are milliseconds.
(function (root) {
  const DEFAULTS = {
    winMs: 200,       // compare the hand with how it was this long ago
    moveT: 0.008,     // change over the window at or above this = moving
    stillT: 0.008,    // change over the window below this = still
    stillMs: 200,     // still for this long = the sign is over (these 200 ms stay in the clip)
    leadMs: 233,      // keep this much before the moment movement was noticed (about 133 ms before the real start)
    missingMs: 267,   // hand gone this long = the sign is over
    minMs: 333,       // a capture shorter than this is a twitch, not a sign
    maxMs: 5000,
  };

  function sharedDelta(a, b) {
    let s = 0, n = 0;
    for (let i = 0; i < a.length; i++) if (a[i] !== 0 && b[i] !== 0) { s += Math.abs(a[i] - b[i]); n++; }
    return n ? s / n : 0;
  }
  // index of the newest frame at least win ms older than t, or -1
  function refIndex(times, t, win) {
    for (let k = times.length - 1; k >= 0; k--) if (times[k] <= t - win) return k;
    return -1;
  }

  class CaptureRule {
    constructor(opts) { this.o = Object.assign({}, DEFAULTS, opts || {}); this.lastDelta = 0; this.reset(); }

    reset() {
      this.bufRows = []; this.bufT = [];        // waiting: recent present frames
      this.capRows = null; this.capT = null;    // capturing
      this.stillStart = null; this.missStart = null;
    }

    get capturing() { return this.capRows !== null; }

    _finish(reason) {
      const rows = this.capRows, times = this.capT;
      this.reset();
      if (times[times.length - 1] - times[0] < this.o.minMs) return null;
      return { frames: rows, times, reason, t0: times[0], t1: times[times.length - 1] };
    }

    // one call per frame. Returns null, or a finished capture {frames, times, reason, t0, t1}.
    push(row, t) {
      const o = this.o;
      if (this.capRows === null) {                                   // ---- waiting for movement
        if (row === null) {
          if (this.bufT.length && t - this.bufT[this.bufT.length - 1] >= o.missingMs) { this.bufRows = []; this.bufT = []; }
          return null;
        }
        this.bufRows.push(row); this.bufT.push(t);
        const horizon = o.winMs + o.leadMs;
        while (this.bufT.length && t - this.bufT[0] > horizon) { this.bufRows.shift(); this.bufT.shift(); }
        const k = refIndex(this.bufT, t, o.winMs);
        if (k >= 0) {
          this.lastDelta = sharedDelta(row, this.bufRows[k]);
          if (this.lastDelta >= o.moveT) {
            const rows = [], times = [];
            for (let i = 0; i < this.bufT.length; i++) if (this.bufT[i] >= t - o.leadMs) { rows.push(this.bufRows[i]); times.push(this.bufT[i]); }
            this.capRows = rows; this.capT = times; this.bufRows = []; this.bufT = [];
            this.stillStart = null; this.missStart = null;
          }
        }
        return null;
      }
      // ---- capturing
      if (row !== null) {
        this.missStart = null;
        this.capRows.push(row); this.capT.push(t);
        const k = refIndex(this.capT, t, o.winMs);
        if (k >= 0) {
          this.lastDelta = sharedDelta(row, this.capRows[k]);
          if (this.lastDelta < o.stillT) { if (this.stillStart === null) this.stillStart = t; }
          else this.stillStart = null;
          if (this.stillStart !== null && t - this.stillStart >= o.stillMs) return this._finish("still");
        }
      } else {
        if (this.missStart === null) this.missStart = t;
        if (t - this.missStart >= o.missingMs) return this._finish("hand_gone");
      }
      if (t - this.capT[0] >= o.maxMs) return this._finish("max");
      return null;
    }
  }

  root.CaptureRule = CaptureRule;
})(typeof window !== "undefined" ? window : globalThis);
