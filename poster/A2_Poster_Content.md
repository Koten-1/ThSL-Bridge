# ThSL Bridge — A2 Poster Content
### ระบบแปลภาษามือไทยสู่ภาษาพูดแบบเรียลไทม์ | Real-time Thai Sign Language Translation System

> Content drafted for 3 poster sections: **Abstract, Materials & Methods, Results**.
> Each section is given in English (poster-ready, concise) with a short Thai gloss below key lines for the presenter.

---

## Abstract

ThSL Bridge is an AI-powered system that translates isolated Thai Sign Language (ThSL) gestures into natural spoken Thai in real time, using nothing but a standard webcam. The system captures hand-landmark sequences with MediaPipe, classifies them with a custom stacked LSTM network, refines the recognized words into grammatical Thai sentences with the Typhoon v2.5 LLM, and finally speaks the result aloud via gTTS. Trained on a self-recorded, group-aware split of 2,664 keypoint sequences (444 originals + augmentation) covering 10 core signs, the model reaches **98.88% test accuracy** on unseen, non-augmented clips. Beyond the numbers, this project demonstrates a full "camera-to-voice" assistive pipeline built to close the everyday communication gap between the Deaf community and hearing people in Thailand — and a disciplined data-science process that caught and corrected a false 99.6%-accuracy result caused by data leakage.

*ThSL Bridge คือระบบ AI ที่แปลภาษามือไทยแบบ isolated เป็นเสียงพูดภาษาไทยธรรมชาติแบบเรียลไทม์ ผ่านกล้องเว็บแคมทั่วไป โดยไม่ต้องใช้อุปกรณ์พิเศษ*

**Keywords:** Thai Sign Language, LSTM, MediaPipe, Assistive Technology, Real-time Recognition, Deaf Communication

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
- Final dataset: **10 target signs** + `none` + `finish` = 12 classes
  - 444 original clips → ×5 augmentation (scale / translate / rotate) → 2,664 total samples

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
