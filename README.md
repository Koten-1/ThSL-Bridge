# ThSL Bridge 🤟
### ระบบแปลภาษามือไทยสู่ภาษาพูดแบบเรียลไทม์
### Real-time Thai Sign Language Translation System

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
---

## Scripts
| ไฟล์ | คำอธิบาย | Description |
|------|----------|-------------|
| `00_Scraper.ipynb` | ดึงข้อมูลจาก th-sl.com | Scrapes ThSL database |
| `extract_keypoints.py` | สกัด Hand Keypoints ด้วย MediaPipe | Extracts hand keypoints |
| `augment_keypoints.py` | เพิ่มข้อมูลด้วย augmentation | Data augmentation |
| `keypoint_stream.py` | สกัด keypoints จากกล้องแบบ real-time | Real-time keypoint extraction |
| `predict_stream.py` | ทำนายท่ามือด้วย LSTM | Real-time sign prediction |

---

## Setup
```bash
# Environment 1 - MediaPipe (keypoint extraction)
conda create -n thsl_env python=3.10
conda activate thsl_env
pip install mediapipe==0.10.14 opencv-python numpy

# Environment 2 - TensorFlow (model inference)
conda create -n thsl_tf_env python=3.10
conda activate thsl_tf_env
pip install tensorflow numpy
```

## Run
```bash
# Terminal 1 - Keypoint extraction
conda activate thsl_env
python scripts/keypoint_stream.py

# Terminal 2 - Sign prediction
conda activate thsl_tf_env
python scripts/predict_stream.py
```

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
