# ThSL Bridge — Innovation / Product

The live, usable side of the project: real-time Thai Sign Language → Thai speech translation, deployed three ways.

## Live demo
**https://koten-1.github.io/ThSL-Bridge/web_app/**

> Note: this link is live against `ThSL-Bridge`'s currently-deployed structure (`web_app/` at repo root). The `research/`+`innovation/` restructure reflected in this repo's own layout hasn't been pushed to `ThSL-Bridge` yet — once it is (and GitHub Pages is repointed if needed), this becomes `.../ThSL-Bridge/innovation/web_app/`.

Runs entirely in-browser via TensorFlow.js + MediaPipe — no install, works on mobile, needs camera permission.
- 📖 Vocabulary tutorial — collapsible panel at the top of the menu, shown before any live mode. Shows the exact 10 trained signs (from `GAME_WORDS`), each with a real ~5s demo clip from `data/raw/` (signer กร, converted to small H.264 `tutorial_clips/sign_00.mp4`..`sign_09.mp4`, index-matched to `GAME_WORDS` order), scoped copy ("these 10 signs, not general ThSL"), and ขอบคุณ flagged as the recommended first try (highest measured reliability — see `SIGN_THRESHOLDS` comments in `predict_stream.py`: correct=1.00, wrong=0.00). Onboarding only, doesn't touch any live-mode logic.
- 🧪 Test mode — sign a word, watch the model predict in real time
- 🎮 Sign Speed Test — a 45-second speed game with a leaderboard
- 🆚 Compare Models — sign once, `pooled-baseline` and `pooled+DANN` (RQ3) predict on the *same* keypoint sequence side by side. 10-way only (no `finish`/`none` — these are research checkpoints, not the shipped 12-way model). Needs `weights_rq3_baseline.json` and `weights_rq3_dann.json` present in this folder (see below) — fails gracefully with an on-screen notice if they're missing.

### Typhoon + TTS in the browser (local testing only)

Test mode's `finish` gesture now calls the Typhoon API directly from the browser (confirmed working — Typhoon's API allows direct browser calls, no CORS issue) and speaks the result via the same endpoint the Python `gTTS` library wraps (confirmed working — plays via a plain `<audio>` element, no key needed for this part).

Needs a local `config.local.js` (gitignored, never committed) setting `window.TYPHOON_API_KEY`:
```bash
cp config.local.example.js config.local.js   # then edit in your real key
```
Missing the file is non-fatal — falls back to showing the raw joined words, same as `postprocess.py`'s graceful degradation.

**Do not deploy this pattern publicly as-is** — the key would be visible to anyone who opens dev tools on a public page. This is fine for local testing on your own machine only; a public deployment would need a backend proxy to hide the key instead.

## Deployment targets

| Folder | Target | Notes |
|---|---|---|
| `web_app/` | GitHub Pages (TF.js, in-browser) | Reconstructs the Keras model in JS from `weights.json`; `convert_model.py`/`export_weights.py` regenerate it from a trained `.h5`/`.keras` checkpoint. `export_weights_rq3.py` does the same for the Compare Models mode — run it after downloading `rq3_pooled_baseline.weights.h5` and `rq3_pooled_dann_signonly.weights.h5` from the export cell in `research/notebooks/🧩RQ3_DANN.ipynb` (Colab), producing `weights_rq3_baseline.json`/`weights_rq3_dann.json` in this same folder |
| `deploy/` | Generic Streamlit deployment | `streamlit_app.py` / `app.py`, self-contained (loads `thsl_model_v6c.weights.h5` alongside itself) |
| `hf_space/` | Hugging Face Spaces | Its own git repo (remote: `huggingface.co/spaces/kachornta22/thsl-bridge`) — push changes there separately from GitHub |

## Real-time pipeline (desktop, two-process)

```
Webcam → MediaPipe (hand keypoints) → LSTM classifier → Typhoon LLM (grammar) → gTTS (voice)
```

```bash
# Terminal 1 — keypoint extraction (needs mediapipe env)
python innovation/keypoint_stream.py

# Terminal 2 — sign prediction + speech (needs tensorflow env)
python innovation/predict_stream.py
```

See the repo-root [README's Setup section](../README.md#setup) for the two-environment setup and Typhoon key placement. `predict_stream.py` imports `postprocess.py` (Typhoon LLM + gTTS) from the same folder — keep them together if you move things around again. All paths in these three scripts are repo-relative, so this still works regardless of where the repo is cloned.

The shared data pipeline (`extract_keypoints.py`, `augment_keypoints.py`, used by both this product's training data and the research notebooks) lives at the repo-root `scripts/`, not here.

## Future direction
Expand vocabulary beyond the current 10 words, deepen real deaf-community use, and extend into other formats (the Sign Speed Test game is the first step into that).
