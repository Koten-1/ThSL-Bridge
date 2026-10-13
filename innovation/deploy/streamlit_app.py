"""
ThSL Bridge — Streamlit demo (video-upload mode)
Upload a clip of one Thai sign → MediaPipe extracts keypoints → LSTM predicts the word.

Run locally:   streamlit run app.py
Deploy:        Hugging Face Spaces (Streamlit SDK) — needs thsl_model_v6c.weights.h5 alongside this file.
"""
import os
import tempfile
import numpy as np
import streamlit as st

# ── Config ──
TARGET_SIGNS = [
    "คนหูหนวก", "คุณ", "ช่วย", "ขอบคุณ",
    "ฉัน", "ต้องการ", "เข้าใจ", "ไม่", "ถาม", "บอก", "finish", "none",
]
SIGN_EN = {
    "คนหูหนวก": "deaf", "คุณ": "you", "ช่วย": "help", "ขอบคุณ": "thank-you",
    "ฉัน": "I/me", "ต้องการ": "want", "เข้าใจ": "understand", "ไม่": "no/not",
    "ถาม": "ask", "บอก": "tell", "finish": "finish", "none": "none",
}
WEIGHTS = os.path.join(os.path.dirname(__file__), "thsl_model_v6c.weights.h5")
COLLECT_FRAMES = 30
MIN_HAND_FRAMES = 15

st.set_page_config(page_title="ThSL Bridge", page_icon="🤟", layout="centered")


# ── Load model once (cached) ──
@st.cache_resource
def load_model():
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    model = Sequential([
        LSTM(32, return_sequences=True, input_shape=(30, 126)),
        Dropout(0.5), LSTM(32), Dropout(0.5),
        Dense(16, activation="relu"), Dense(12, activation="softmax"),
    ])
    model.load_weights(WEIGHTS)
    return model


@st.cache_resource
def get_hands():
    import mediapipe as mp
    return mp.solutions.hands.Hands(
        static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5
    )


def extract_keypoints(video_path, hands):
    """Same logic as extract_keypoints.py — hand-present frames only, resampled to 30."""
    import cv2
    cap = cv2.VideoCapture(video_path)
    frames, total, hand_count = [], 0, 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total += 1
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            hand_count += 1
            lh = np.zeros(63)
            rh = np.zeros(63)
            for lm, hd in zip(results.multi_hand_landmarks, results.multi_handedness):
                coords = np.array([[p.x, p.y, p.z] for p in lm.landmark]).flatten()
                if hd.classification[0].label == "Left":
                    lh = coords
                else:
                    rh = coords
            frames.append(np.concatenate([lh, rh]))
    cap.release()

    hand_pct = hand_count / max(total, 1) * 100
    if len(frames) < MIN_HAND_FRAMES:
        return None, hand_pct, len(frames)

    arr = np.array(frames)
    idx = np.linspace(0, len(arr) - 1, COLLECT_FRAMES, dtype=int)
    return arr[idx], hand_pct, len(frames)


# ── UI ──
st.title("🤟 ThSL Bridge")
st.caption("ระบบแปลภาษามือไทย — อัปโหลดคลิปท่ามือ 1 ท่า แล้วโมเดลจะทำนายคำ")

st.info("รองรับ 10 คำ: คนหูหนวก, คุณ, ช่วย, ขอบคุณ, ฉัน, ต้องการ, เข้าใจ, ไม่, ถาม, บอก")

uploaded = st.file_uploader("อัปโหลดคลิปท่าภาษามือ (.mp4)", type=["mp4", "mov", "avi"])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded.read())
        video_path = tmp.name

    st.video(video_path)

    with st.spinner("กำลังสกัด keypoint และทำนาย..."):
        hands = get_hands()
        keypoints, hand_pct, n_hand = extract_keypoints(video_path, hands)

        st.write(f"🖐️ ตรวจจับมือได้ **{hand_pct:.0f}%** ของเฟรม ({n_hand} เฟรมที่มีมือ)")

        if keypoints is None:
            st.error(
                f"ตรวจจับมือได้น้อยเกินไป (ต้องมีอย่างน้อย {MIN_HAND_FRAMES} เฟรม) "
                "ลองอัดให้เห็นมือชัด ๆ ตลอดคลิป"
            )
        else:
            model = load_model()
            pred = model.predict(np.expand_dims(keypoints, 0), verbose=0)[0]
            top_idx = int(np.argmax(pred))
            sign = TARGET_SIGNS[top_idx]
            conf = float(pred[top_idx])

            if sign == "none":
                st.warning(f"โมเดลคิดว่าไม่มีท่าภาษามือ (none) — ความมั่นใจ {conf:.0%}")
            else:
                st.success(f"### ผลทำนาย: **{sign}** ({SIGN_EN.get(sign, '')})")
                st.metric("ความมั่นใจ", f"{conf:.0%}")

            # Top-3 bar
            st.write("#### 3 อันดับที่เป็นไปได้")
            order = np.argsort(pred)[::-1][:3]
            for i in order:
                label = TARGET_SIGNS[i]
                st.write(f"{label} ({SIGN_EN.get(label, '')})")
                st.progress(float(pred[i]))

    os.unlink(video_path)

st.divider()
st.caption("ThSL Bridge — Stacked LSTM + MediaPipe | by Kachorn (AI Builders 2026)")
