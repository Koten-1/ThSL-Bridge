# ThSL Bridge 🤟
### ระบบแปลภาษามือไทยสู่ภาษาพูดแบบเรียลไทม์
### Real-time Thai Sign Language Translation System

---

## 🎮 เล่นเลย! | Live Demo (ไม่ต้องลงอะไร)

**▶️ เปิดเล่นในเบราว์เซอร์ได้ทันที:**
### 👉 https://koten-1.github.io/ThSL-Bridge/web_app/

- 🧪 **โหมดทดสอบ** — ทำท่าภาษามือ ดูโมเดลทายแบบเรียลไทม์
- 🎮 **Sign Speed Test** — เกมทำท่าให้เร็วที่สุดใน 45 วินาที + Leaderboard

> รันด้วย TensorFlow.js + MediaPipe ในเบราว์เซอร์ (มือถือก็เล่นได้) • ต้องอนุญาตกล้อง

---

## Repository structure

This project has two parallel tracks:

| Folder | Contents |
|---|---|
| [`research/`](research/README.md) | The academic side — RQ1 (leakage audit), RQ2 (architecture comparison), RQ3 (zero-shot signer generalization + domain-adversarial training), study notes, figures |
| [`innovation/`](innovation/README.md) | The live product — the web app + game (GitHub Pages), Streamlit deployments, the real-time webcam→speech pipeline |
| `scripts/` | Shared data pipeline (`extract_keypoints.py`, `augment_keypoints.py`) used by both tracks |

---

## ภาพรวมโครงงาน | Project Overview

**ภาษาไทย:**
ThSL Bridge คือนวัตกรรมที่ใช้ปัญญาประดิษฐ์แปลภาษามือไทย (ThSL) เป็นประโยคภาษาไทยธรรมชาติพร้อมเสียงพูดแบบเรียลไทม์ผ่านกล้องอุปกรณ์ทั่วไป พัฒนาขึ้นเพื่อลดช่องว่างการสื่อสารระหว่างผู้พิการทางการได้ยินกับคนทั่วไปในสังคมไทย

**English:**
ThSL Bridge is an AI-powered system that translates Thai Sign Language (ThSL) into natural Thai speech in real-time using a standard webcam. Developed to bridge the communication gap between the deaf community and hearing people in Thailand.

---

## Pipeline
Webcam → MediaPipe (Hand Keypoints) → LSTM Model → Typhoon LLM → gTTS (Voice)

---
## คำศัพท์ที่รองรับ | Supported Signs (v1.0)

| # | ภาษามือไทย | ความหมาย |
|---|-----------|---------|
| 1 | คนหูหนวก | Deaf person |
| 2 | คุณ | You |
| 3 | ช่วย | Help |
| 4 | ขอบคุณ | Thank you |
| 5 | คำถาม | Question |
| 6 | ฉัน | I / Me |
| 7 | ต้องการ | Want / Need |
| 8 | เข้าใจ | Understand |
| 9 | ไม่ | No |
| 10 | ถาม | Ask |

> 🎯 เป้าหมาย v2.0: ขยายเป็น 20+ คำครอบคลุมการสื่อสารพื้นฐาน
---

## ผลลัพธ์ | Results
- 10 คำศัพท์ภาษามือไทย | 10 Thai Sign Language words
- ความแม่นยำ 89% | 89% validation accuracy  
- 654 ตัวอย่างหลัง augmentation | 654 training samples after augmentation
- Real-time inference ผ่านกล้องเว็บแคม | Real-time webcam inference

---

## สถาปัตยกรรมระบบ | System Architecture
```text
┌─────────────────────────────────────────────────────┐
│                     ThSL Bridge                     │
├─────────────────────────────────────────────────────┤
│  📷 Webcam Input                                    │
│      │                                              │
│      ▼                                              │
│  🖐 MediaPipe Hand Landmark Detection (21 pts/hand)  │
│      │                                              │
│      ▼                                              │
│  📊 Keypoint Sequence (30 frames × 126 values)      │
│      │                                              │
│      ▼                                              │
│  🧠 2-Layer LSTM Classifier (10 signs, 89% acc)     │
│      │                                              │
│      ▼                                              │
│  💬 Typhoon v2.5 LLM (Natural Thai Grammar)        │
│      │                                              │
│      ▼                                              │
│  🔊 gTTS Voice Output                               │
└─────────────────────────────────────────────────────┘
```
---

## Scripts
| ไฟล์ | คำอธิบาย | Description |
|------|----------|-------------|
| `scripts/extract_keypoints.py` | สกัด Hand Keypoints ด้วย MediaPipe | Extracts hand keypoints (shared by research + product) |
| `scripts/augment_keypoints.py` | เพิ่มข้อมูลด้วย augmentation | Data augmentation (shared by research + product) |
| `innovation/keypoint_stream.py` | สกัด keypoints จากกล้องแบบ real-time | Real-time keypoint extraction |
| `innovation/predict_stream.py` | ทำนายท่ามือด้วย LSTM | Real-time sign prediction |

See [`innovation/README.md`](innovation/README.md) for the full pipeline and deployment details, and [`research/README.md`](research/README.md) for the RQ1/RQ2/RQ3 methodology.

---

## Setup
Two isolated Python environments — MediaPipe and TensorFlow pull in conflicting
dependency versions (protobuf) if installed together. Conda works too, but plain
`venv` needs no separate installer and is what's verified working (macOS,
Apple Silicon, Python 3.12):

```bash
# Environment 1 - MediaPipe (keypoint extraction)
python3 -m venv ~/.thsl-tools/mediapipe_venv
~/.thsl-tools/mediapipe_venv/bin/pip install mediapipe==0.10.14 opencv-python numpy pillow

# Environment 2 - TensorFlow (model inference + Typhoon + gTTS)
python3 -m venv ~/.thsl-tools/tf_venv
~/.thsl-tools/tf_venv/bin/pip install tensorflow numpy gTTS
```

All paths in `keypoint_stream.py`/`predict_stream.py`/`postprocess.py` are
repo-relative (computed from each script's own location), so the repo can live
anywhere — no path editing needed.

> `mediapipe==0.10.14` is a hard pin, not a suggestion: `mediapipe>=1.0.0` dropped
> the legacy `mp.solutions.hands` API entirely (only `Image`/`ImageFormat`/`tasks`
> remain), which `keypoint_stream.py` uses throughout. Installing latest breaks
> with `AttributeError: module 'mediapipe' has no attribute 'solutions'`.

Typhoon API key (for sentence-forming in `postprocess.py`): put it in either
the `TYPHOON_API_KEY` environment variable, or a file `innovation/typhoon_key.txt`
(one line, just the key — gitignored, never commit it).

## Run
```bash
# Terminal 1 - Keypoint extraction
~/.thsl-tools/mediapipe_venv/bin/python innovation/keypoint_stream.py

# Terminal 2 - Sign prediction + Typhoon + speech
~/.thsl-tools/tf_venv/bin/python innovation/predict_stream.py
```

macOS will prompt for camera permission the first time Terminal 1 runs —
allow it, or enable manually under System Settings → Privacy & Security → Camera.

---

## Tech Stack
| Tool | Version | Purpose |
|------|---------|---------|
| MediaPipe | 0.10.14 | Hand landmark detection |
| TensorFlow/Keras | 2.21 | LSTM model training |
| Typhoon | v2.5-30b | Thai grammar correction |
| gTTS | latest | Thai text-to-speech |
| Data source | NADT | th-sl.com official ThSL database |

---

## Developer
**Kachornattaphon Khumyaito**  + Claude
GitHub: [@Koten-1](https://github.com/Koten-1)
