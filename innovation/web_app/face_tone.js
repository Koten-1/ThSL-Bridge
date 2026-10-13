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

  // Loaded lazily so ToneRules can be used and tested without any network.
  async function createFaceTracker() {
    const mp = await import(MP_BUNDLE);
    const vision = await mp.FilesetResolver.forVisionTasks(MP_BUNDLE + "/wasm");
    const landmarker = await mp.FaceLandmarker.createFromOptions(vision, {
      baseOptions: { modelAssetPath: FACE_MODEL },
      runningMode: "VIDEO",
      numFaces: 1,
      outputFaceBlendshapes: true,
      outputFacialTransformationMatrixes: true,
    });

    return {
      // Returns the raw per-frame numbers, or null when no face is visible.
      detect(video, tMs) {
        const res = landmarker.detectForVideo(video, tMs);
        if (!res.faceBlendshapes?.length || !res.facialTransformationMatrixes?.length) return null;
        const s = {};
        for (const c of res.faceBlendshapes[0].categories) s[c.categoryName] = c.score;
        const avg = (...k) => k.reduce((sum, n) => sum + (s[n] || 0), 0) / k.length;
        return {
          browRaise: avg("browInnerUp", "browOuterUpLeft", "browOuterUpRight"),
          browFurrow: avg("browDownLeft", "browDownRight"),
          mouthFrown: avg("mouthFrownLeft", "mouthFrownRight"),
          ...anglesFromMatrix(res.facialTransformationMatrixes[0].data),
        };
      },
    };
  }

  root.FaceTone = { DEFAULTS, ToneRules, meanOf, anglesFromMatrix, createFaceTracker };
})(typeof window !== "undefined" ? window : globalThis);
