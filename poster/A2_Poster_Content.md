# ThSL Bridge — A2 Poster Content
### ระบบแปลภาษามือไทยสู่ภาษาพูดแบบเรียลไทม์ | Real-time Thai Sign Language Translation System

> Content drafted for 4 poster sections: **Abstract, Introduction & Motivation, Materials & Methods, Results**.
> Each section is given in English (poster-ready, concise) with a short Thai gloss below key lines for the presenter.

---

## Abstract

ThSL Bridge is an AI-powered system that translates isolated Thai Sign Language (ThSL) gestures into natural spoken Thai in real time, using nothing but a standard webcam. The system captures hand-landmark sequences with MediaPipe, classifies them with a custom stacked LSTM network, refines the recognized words into grammatical Thai sentences with the Typhoon v2.5 LLM, and finally speaks the result aloud via gTTS. Trained on a self-recorded, group-aware split of 2,664 keypoint sequences (444 originals + augmentation) covering 10 core signs, the model reaches **98.88% test accuracy** on unseen, non-augmented clips. Beyond the numbers, this project demonstrates a full "camera-to-voice" assistive pipeline built to close the everyday communication gap between the Deaf community and hearing people in Thailand — and a disciplined data-science process that caught and corrected a false 99.6%-accuracy result caused by data leakage.

*ThSL Bridge คือระบบ AI ที่แปลภาษามือไทยแบบ isolated เป็นเสียงพูดภาษาไทยธรรมชาติแบบเรียลไทม์ ผ่านกล้องเว็บแคมทั่วไป โดยไม่ต้องใช้อุปกรณ์พิเศษ*

**Keywords:** Thai Sign Language, LSTM, MediaPipe, Assistive Technology, Real-time Recognition, Deaf Communication

---

## Introduction & Motivation

### The communication gap
Thailand is home to a large Deaf and hard-of-hearing community, yet Thai Sign Language (ThSL) interpreters remain scarce and hearing Thais rarely learn ThSL. This leaves everyday interactions — asking for help, answering a question, saying thank you — dependent on writing notes, typing on a phone, or the presence of a trained interpreter. That gap is exactly what this project targets: turning a hand gesture, captured by an ordinary webcam, directly into a spoken Thai sentence, with no interpreter and no specialized hardware required.

*ประเทศไทยมีชุมชนผู้พิการทางการได้ยินจำนวนมาก แต่ล่ามภาษามือมีจำกัด และคนหูดีส่วนใหญ่ไม่เข้าใจภาษามือไทย ทำให้การสื่อสารในชีวิตประจำวันเป็นอุปสรรค*

### Why this is a hard problem
- **Sign language is not a static image problem, it is a sequence problem.** A single sign unfolds as a short *movement* over time, so a system must model temporal structure, not just recognize a single frame.
- **No pre-trained models exist for this input type.** ThSL has far less public data than spoken/written Thai NLP, and existing image-classification models (trained on photos, not hand-keypoint sequences) do not transfer — the recognizer had to be built from scratch.
- **Public ThSL reference data is unreliable for computer vision.** The team's own inspection tooling found that clips scraped from the official th-sl.com database were only detectable by hand-tracking 29–62% of the time (motion blur, occlusion, camera angle), versus ~100% for purpose-recorded clips — meaning a naive "just scrape more data" approach would have quietly poisoned the model.

### Project goals
1. Recognize a first set of **10 common ThSL signs** (e.g. "help", "thank you", "understand", "want") from live webcam video, in real time.
2. Go beyond isolated word recognition: assemble recognized signs into a **grammatically natural spoken Thai sentence**, not just a word-by-word gloss.
3. Build and validate the system as a genuinely **deployable tool** — including a zero-install, browser-based demo — rather than a lab-only accuracy benchmark.
4. Practice and demonstrate a **rigorous ML workflow**: questioning suspiciously high accuracy, checking for data leakage, and verifying train/inference consistency, rather than accepting the first good-looking number.

---

## Materials & Methods

### 1. Problem framing
- Task type: **Sequence classification** — specifically Isolated Sign Language Recognition (ISLR)
- Learning paradigm: Supervised learning (each clip labeled by its source folder name)
- Model built **from scratch** (no transfer learning available for ThSL keypoint sequences)

### 2. Pipeline
```
Webcam → MediaPipe (Hand Keypoints) → LSTM Classifier → Typhoon LLM (grammar) → gTTS (voice)
```

### 3. Data collection
- Primary source considered: **th-sl.com** (NADT's official ThSL reference database), scraped via `00_Scraper.ipynb`
- Data-quality check with a custom tool (`inspect_sign.py`) measuring **hand-detection rate**: scraped clips only reached **29–62%** hand-detection (MediaPipe frequently failed to find hands), vs. **100%** for self-recorded clips → scraped data was rejected as unusable, and the team recorded its own clips instead
- **Recording setup:** 1080p, 30 fps, 40 clips per sign word
  - 10 clips/sign recorded with a handheld smartphone camera
  - 30 clips/sign recorded with a Logitech BRIO 300 webcam
- Final dataset: **10 target signs** + `none` + `finish` = 12 classes
  - Original clips split **before** augmentation (group-aware, 80/20): **255 original clips → train**, **89 original clips → held-out test**
  - Augmentation applied only to the 255 training originals → **1,775 augmented clips**
  - Train set = 255 + 1,775 = **2,030 sequences**; Test set = **89 sequences** (100% original, unaugmented, never seen during training)

#### `extract_keypoints.py` — turning raw video into training data
This script is the bridge between a raw recorded video and a usable training sample, and its correctness is what everything downstream depends on:
1. Runs **MediaPipe Hands** (`max_num_hands=2, min_detection_confidence=0.5`) over the clip frame by frame.
2. For each frame, builds a **126-value vector**: 63 values for the left hand + 63 for the right hand (21 landmarks × x, y, z each).
3. **Keeps a frame only if at least one hand was actually detected** (`if results.multi_hand_landmarks:`) — frames with no hand present are dropped entirely rather than saved as all-zero rows. This was a deliberate fix: an earlier version appended *every* frame regardless of hand presence, polluting the data with "empty" frames and teaching the model to over-predict certain signs whenever no hand was visible.
4. Clips with fewer than **15 valid hand-frames** are rejected outright as unusable recordings (`MIN_HAND_FRAMES = 15`).
5. The remaining hand-frames (count varies clip to clip, since gestures take different amounts of time) are **resampled to a fixed 30 frames** using `np.linspace` indices — so every saved sequence has the same shape **(30, 126)**, matching what the LSTM expects.
6. Output: one `.npy` file per clip in `data/processed/<sign>/`, ready to feed directly into training.

**Why it matters:** this "only real hand frames, then resample to 30" rule is re-implemented identically in the live `keypoint_stream.py` used for webcam inference — guaranteeing **train/serve consistency**, one of the project's key lessons (see Discussion).

### 4. Feature extraction
- **MediaPipe Hands**: 21 landmarks/hand × 2 hands × 3 coords = **126 values per frame**
- Only frames where a hand is actually detected are kept (empty/zero frames are discarded — a key bug-fix versus an earlier "leaky" extractor)
- Each gesture clip is resampled to a fixed length of **30 frames** (linspace resampling) so sequence length matches between training and live inference

### 5. Model architecture — Stacked LSTM
```python
model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),  # learns sub-movements
    Dropout(0.5),
    LSTM(32),                                                 # combines into a full gesture
    Dropout(0.5),
    Dense(16, activation='relu'),
    Dense(12, activation='softmax')                           # 12 classes
])
```
- LSTM chosen because sign language is a time sequence requiring memory (forget / input / output gates); supported by prior research (Springer, 2024) showing LSTM outperforming plain RNN, Bi-LSTM, and FNN-LSTM baselines on similar tasks
- Stacked (2-layer) design lets the network learn a movement→gesture hierarchy, controlled against overfitting with 32 units/layer + 0.5 dropout

### 6. Training protocol
- Optimizer: **Adam**; Loss: **sparse categorical crossentropy**
- **EarlyStopping** (patience = 20, restore best weights) — training stopped at epoch 93
- **Group-aware train/test split** to prevent data leakage: original clips are split first (80/20), then each original's augmented copies are forced into the *same* split as their source clip
  - Train: 2,130 sequences | Test: 89 sequences (originals only, no augmented "twins")

### 7. Deployment
- Real-time inference via two cooperating processes (`keypoint_stream.py` → `predict_stream.py`) using a **confidence threshold + vote window** to stabilize predictions
- Recognized sign sequence is passed to **Typhoon v2.5-30B** for natural Thai sentence formation, then **gTTS** for speech output
- A browser-based demo (TensorFlow.js + MediaPipe) is also deployed for zero-install testing: https://koten-1.github.io/ThSL-Bridge/web_app/

---

## Results

| Metric | Value |
|---|---|
| Target signs (v1.0) | 10 words |
| Total classes (incl. `none`, `finish`) | 12 |
| Original recorded clips | 444 |
| Augmented samples | 2,220 (×5) |
| Total dataset size | 2,664 |
| Training set | 2,130 |
| Test set (originals only) | 89 |
| **Test accuracy (honest, group-aware split)** | **98.88%** |
| Naive split accuracy (before leakage fix) | 99.6% *(discarded — inflated)* |
| Scraped-data hand-detection rate | 29–62% *(rejected)* |
| Self-recorded hand-detection rate | 100% |

**Key findings:**
- **Data-leakage correction:** An initial naive train/test split (mixing originals and their augmented copies before splitting) produced a suspiciously high 99.6% accuracy. A group-aware split — keeping each original clip and all its augmented variants on the same side of the split — revealed the true, honest performance of **98.88%** on a 89-clip, augmentation-free test set.
- **EDA caught a confusable pair in advance:** feature-distance analysis between `none` and `คุณ` ("you") showed a small separation (distance ≈ 1.55), correctly predicting that these two classes would be the most likely to be confused — confirmed in the confusion matrix (`confusion_matrix_v6c_thai.png`).
- **Train/serve consistency mattered more than the model:** the real-time predictor produced nonsensical results (defaulting to "ขอบคุณ/thank you") until the live keypoint extractor was fixed to match the training-time extractor exactly (dropping empty/zero frames, resampling to 30 frames) — the model itself never changed.
- The system runs **fully in real time** end-to-end (webcam → recognized word → spoken Thai sentence), validated with a live webcam demo and a browser-only (TensorFlow.js) build for judges/visitors to try hands-on.

*(See `confusion_matrix_v6c_thai.png` and `scraped_vs_own_handdetection.png` in the repo root for the visual assets referenced above — recommended for direct placement in the Results panel of the poster.)*
