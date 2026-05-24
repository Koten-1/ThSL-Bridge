# ThSL Bridge 🤟
### Real-time Thai Sign Language Translation System

AI-powered pipeline that converts Thai Sign Language (ThSL) into natural Thai speech in real-time.

## Pipeline

## Results
- 10 Thai Sign Language words
- 89% validation accuracy
- 654 training samples (after augmentation)

## Scripts
| File | Description |
|------|-------------|
| `00_Scraper.ipynb` | Scrapes ThSL database (th-sl.com) |
| `extract_keypoints.py` | Extracts hand keypoints using MediaPipe |
| `augment_keypoints.py` | Data augmentation (scale, rotate, translate, flip) |
| `keypoint_stream.py` | Real-time webcam keypoint extraction |
| `predict_stream.py` | Real-time sign prediction using LSTM |

## Setup
```bash
# Environment 1 - MediaPipe
conda activate thsl_env
pip install mediapipe==0.10.14 opencv-python numpy

# Environment 2 - TensorFlow  
conda activate thsl_tf_env
pip install tensorflow numpy
```

## Run
```bash
# Terminal 1
conda activate thsl_env
python scripts/keypoint_stream.py

# Terminal 2
conda activate thsl_tf_env
python scripts/predict_stream.py
```

## Tech Stack
- MediaPipe 0.10.14 — Hand landmark detection
- TensorFlow/Keras — LSTM model training
- Typhoon v2.5 — Thai grammar correction
- gTTS — Thai text-to-speech
- Data source: NADT (th-sl.com)
