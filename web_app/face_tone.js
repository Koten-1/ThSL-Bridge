// Face tone for ThSL Bridge: is the signer asking or telling, and is it a yes or a no?
//
// Plain script on purpose (no import/export): a page opened by double-click (file://)
// can load this with <script src="face_tone.js">, while browsers block ES modules there.
// Everything is exposed as one global: FaceTone.
//
// Two separate pieces:
//   ToneRules         pure rules over numbers, no camera, no network, easy to test
//   createFaceTracker wraps MediaPipe's pretrained Face Landmarker, nothing is trained here
//
// The thresholds are provisional. The deaf club told us the face is the "punctuation"
// of ThSL, but not yet which exact movements, so every cue is exposed separately and the
// test page lets you tune it on real people before anything is trusted.
(function (root) {
  const DEFAULTS = {
    raiseThresh: 0.25,   // brow raise above the signer's own neutral face (0..1)
    furrowThresh: 0.25,  // brow furrow above neutral (0..1)
    shakeSwingDeg: 5,    // head must turn at least this far each way to count as a swing
    nodSwingDeg: 4,
    minReversals: 2,     // left-right-left is 2 reversals
    windowMs: 1500,      // look back this far for shakes and nods
    smooth: 0.35,        // exponential smoothing for blendshape scores (higher = faster)
  };

  function countReversals(values, minSwing) {
    if (values.length < 3) return 0;
    let reversals = 0, dir = 0, ref = values[0];
    for (const v of values) {
      if (dir >= 0 && v < ref - minSwing) { if (dir !== 0) reversals++; dir = -1; ref = v; }
      else if (dir <= 0 && v > ref + minSwing) { if (dir !== 0) reversals++; dir = 1; ref = v; }
      else if (dir === 1 && v > ref) ref = v;
      else if (dir === -1 && v < ref) ref = v;
    }
    return reversals;
  }

  class ToneRules {
    constructor(opts = {}) {
      this.o = { ...DEFAULTS, ...opts };
      this.base = { browRaise: 0, browFurrow: 0 };
      this.sm = null;
      this.hist = [];
    }

    // f: { browRaise, browFurrow, mouthFrown, yaw, pitch, roll }, angles in degrees
    push(f, tMs) {
      const a = this.o.smooth;
      this.sm = this.sm
        ? {
            browRaise: this.sm.browRaise + a * (f.browRaise - this.sm.browRaise),
            browFurrow: this.sm.browFurrow + a * (f.browFurrow - this.sm.browFurrow),
            mouthFrown: this.sm.mouthFrown + a * (f.mouthFrown - this.sm.mouthFrown),
          }
        : { browRaise: f.browRaise, browFurrow: f.browFurrow, mouthFrown: f.mouthFrown };

      this.hist.push({ t: tMs, yaw: f.yaw, pitch: f.pitch });
      while (this.hist.length && tMs - this.hist[0].t > this.o.windowMs) this.hist.shift();

      const raise = this.sm.browRaise - this.base.browRaise;
      const furrow = this.sm.browFurrow - this.base.browFurrow;
      const questionLike = raise > this.o.raiseThresh || furrow > this.o.furrowThresh;

      const yawRev = countReversals(this.hist.map(h => h.yaw), this.o.shakeSwingDeg);
      const pitchRev = countReversals(this.hist.map(h => h.pitch), this.o.nodSwingDeg);
      const shake = yawRev >= this.o.minReversals;
      // turning the head also wobbles pitch a little, so a nod only counts when it is not a shake
      const nod = !shake && pitchRev >= this.o.minReversals;

      return {
        tone: questionLike ? "question" : "statement",
        polarity: shake ? "negative" : "positive",
        cue: !questionLike ? null : (raise >= furrow ? "brow raise" : "brow furrow"),
        shake, nod,
        raise, furrow, yawRev, pitchRev,
        smoothed: { ...this.sm },
      };
    }

    setBaseline(b) { this.base = { ...this.base, ...b }; }
    reset() { this.sm = null; this.hist = []; }
  }

  // Face reading for one word. samples: [{ t, raise, furrow, yaw, pitch }] taken while the face was visible
  // (raise and furrow are already measured against the person's neutral face).
  // Everything is judged only from the time the sign was being made (t0..t1) plus a short lead-in, so a shake or a raised
  // brow from the previous word cannot carry over. Uses the same thresholds as ToneRules (pass toneRules.o as opts).
  function summarize(samples, t0, t1, opts) {
    const o = Object.assign({}, DEFAULTS, { lookbackMs: 300, minSamples: 3, questionFrac: 0.4 }, opts || {});
    const s = samples.filter(x => x.t >= t0 - o.lookbackMs && x.t <= t1);
    if (s.length < o.minSamples) return { seen: false, n: s.length, question: false, negative: false, nod: false };
    const marked = s.filter(x => x.raise > o.raiseThresh || x.furrow > o.furrowThresh).length / s.length;
    const yawRev = countReversals(s.map(x => x.yaw), o.shakeSwingDeg);
    const pitchRev = countReversals(s.map(x => x.pitch), o.nodSwingDeg);
    const negative = yawRev >= o.minReversals;
    return { seen: true, n: s.length, question: marked >= o.questionFrac, negative,
             nod: !negative && pitchRev >= o.minReversals, qFrac: marked, yawRev, pitchRev };
  }

  // The face tags decide the meaning by plain rules (no AI): a question adds the particle at the end,
  // a head shake puts the negation word in front of that word. words: [{ sign, face }]. Returns a list of strings.
  function applyFaceRules(words, opts) {
    const o = Object.assign({ negation: "ไม่", question: "ไหม" }, opts || {});
    const out = [];
    let asked = false;
    for (const w of words) {
      const f = w.face;
      if (f && f.negative && w.sign !== o.negation && out[out.length - 1] !== o.negation) out.push(o.negation);
      out.push(w.sign);
      if (f && f.question) asked = true;
    }
    if (asked) out.push(o.question);
    return out;
  }

  function meanOf(rows, key) {
    return rows.length ? rows.reduce((s, r) => s + r[key], 0) / rows.length : 0;
  }

  // Rotation of the face relative to the camera, from MediaPipe's 4x4 column-major matrix.
  function anglesFromMatrix(d) {
    const s = Math.hypot(d[0], d[1], d[2]) || 1;     // matrix may carry a uniform scale
    const r00 = d[0] / s, r10 = d[1] / s, r20 = d[2] / s, r21 = d[6] / s, r22 = d[10] / s;
    const deg = 180 / Math.PI;
    return {
      yaw: -Math.asin(Math.max(-1, Math.min(1, r20))) * deg,
      pitch: Math.atan2(r21, r22) * deg,
      roll: Math.atan2(r10, r00) * deg,
    };
  }

  const MP_BUNDLE = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0";
  const FACE_MODEL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

  // Per-frame numbers for face i of a MediaPipe result, or null when the model did not output them.
  function featuresOf(res, i) {
    const bs = res.faceBlendshapes && res.faceBlendshapes[i];
    const mat = res.facialTransformationMatrixes && res.facialTransformationMatrixes[i];
    if (!bs || !mat) return null;
    const s = {};
    for (const c of bs.categories) s[c.categoryName] = c.score;
    const avg = (...k) => k.reduce((sum, n) => sum + (s[n] || 0), 0) / k.length;
    return {
      browRaise: avg("browInnerUp", "browOuterUpLeft", "browOuterUpRight"),
      browFurrow: avg("browDownLeft", "browDownRight"),
      mouthFrown: avg("mouthFrownLeft", "mouthFrownRight"),
      ...anglesFromMatrix(mat.data),
    };
  }

  // Loaded lazily so ToneRules can be used and tested without any network.
  // opts.numFaces: how many faces to find (1 for the tone test, more for person focus).
  // opts.blendshapes / opts.matrices: set false when only face boxes are needed (lighter and faster).
  async function createFaceTracker(opts) {
    const o = Object.assign({ numFaces: 1, blendshapes: true, matrices: true }, opts || {});
    const mp = await import(MP_BUNDLE);
    const vision = await mp.FilesetResolver.forVisionTasks(MP_BUNDLE + "/wasm");
    const make = delegate => mp.FaceLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: FACE_MODEL, delegate },
      runningMode: "VIDEO",
      numFaces: o.numFaces,
      outputFaceBlendshapes: o.blendshapes,
      outputFacialTransformationMatrixes: o.matrices,
    });
    // the web default is the CPU; use the GPU when the browser allows it
    let landmarker;
    try { landmarker = await make("GPU"); }
    catch (e) { console.warn("[face] GPU delegate failed, using CPU", e); landmarker = await make("CPU"); }

    return {
      close() { landmarker.close(); },
      // First face's raw per-frame numbers, or null when no face is visible.
      detect(video, tMs) {
        return featuresOf(landmarker.detectForVideo(video, tMs), 0);
      },
      // Every face found: [{ box: {x, y, w, h} normalized, features or null }].
      detectFaces(video, tMs) {
        const res = landmarker.detectForVideo(video, tMs);
        return (res.faceLandmarks || []).map((lm, i) => {
          let x0 = 1, y0 = 1, x1 = 0, y1 = 0;
          for (const p of lm) {
            if (p.x < x0) x0 = p.x; if (p.x > x1) x1 = p.x;
            if (p.y < y0) y0 = p.y; if (p.y > y1) y1 = p.y;
          }
          return { box: { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }, features: featuresOf(res, i) };
        });
      },
    };
  }

  root.FaceTone = { DEFAULTS, ToneRules, meanOf, anglesFromMatrix, summarize, applyFaceRules, createFaceTracker };
})(typeof window !== "undefined" ? window : globalThis);
