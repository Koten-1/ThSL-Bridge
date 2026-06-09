import os

# Redirect ALL temp/cache writes away from C:\ before TensorFlow loads
os.environ["TMP"]                    = "D:/KachornThSL/tmp"
os.environ["TEMP"]                   = "D:/KachornThSL/tmp"
os.environ["TF_CPP_MIN_LOG_LEVEL"]   = "3"      # silence TF C++ logs
os.environ["TF_ENABLE_ONEDNN_OPTS"]  = "0"      # silence oneDNN messages
os.makedirs("D:/KachornThSL/tmp", exist_ok=True)

import numpy as np
import time
import json
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

TARGET_SIGNS = [
    "คนหูหนวก", "คุณ", "ช่วย", "ขอบคุณ",
    "คำถาม", "ฉัน", "ต้องการ", "เข้าใจ", "ไม่", "ถาม", "none"
]

# English labels for terminal display (PowerShell can't show Thai)
SIGN_EN = {
    "คนหูหนวก": "deaf",
    "คุณ":      "you",
    "ช่วย":     "help",
    "ขอบคุณ":   "thank-you",
    "คำถาม":    "question",
    "ฉัน":      "I/me",
    "ต้องการ":  "want",
    "เข้าใจ":   "understand",
    "ไม่":      "no/not",
    "ถาม":      "ask",
    "none":     "none",
}

SIGN_THRESHOLDS = {
    # gap=0.86 — safe, set comfortably above wrong_conf (0.00)
    "คนหูหนวก": 0.82,
    # gap=-0.01 — BROKEN: wrong is MORE confident than correct, set very high to at least reduce false positives
    "คุณ":      0.97,
    # gap=0.98 — perfect, easy
    "ช่วย":     0.92,
    # gap=1.00 — perfect
    "ขอบคุณ":   0.92,
    # gap=0.61 — good: 0.32 + 0.61*0.6 = 0.69
    "คำถาม":    0.69,
    # gap=0.43 — decent: 0.49 + 0.43*0.6 = 0.75
    "ฉัน":      0.75,
    # gap=0.32 — moderate: 0.64 + 0.32*0.6 = 0.83
    "ต้องการ":  0.83,
    # gap=0.37 — moderate: 0.61 + 0.37*0.6 = 0.83
    "เข้าใจ":   0.83,
    # gap=0.00 — BROKEN: no separation, set at correct_conf as best we can do
    "ไม่":      0.73,
    # gap=0.02 — nearly broken: set just above wrong_conf
    "ถาม":      0.76,
    # gap=0.99 — perfect
    "none":     0.95,
}

VOTE_WINDOW = 8   # look at last N predictions
VOTE_NEEDED = 5   # sign must appear this many times in that window to confirm
KEYPOINTS_PATH = "D:/KachornThSL/temp/keypoints.npy"
FINISH_PATH    = "D:/KachornThSL/temp/finish.txt"
RESULT_PATH    = "D:/KachornThSL/temp/result.txt"
TOPN_PATH      = "D:/KachornThSL/temp/topn.json"

model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),
    Dropout(0.5),
    LSTM(32),
    Dropout(0.5),
    Dense(16, activation='relu'),
    Dense(11, activation='softmax')
])

model.load_weights("D:/KachornThSL/models/thsl_model_v5.weights.h5")
print("Model loaded!")
print("Waiting for signs...")

# Clean up stale temp files from previous sessions
for _stale in [KEYPOINTS_PATH, FINISH_PATH, RESULT_PATH, TOPN_PATH]:
    if os.path.exists(_stale):
        os.remove(_stale)
        print(f"Cleaned stale: {_stale}")

last_keypoints_modified = 0
last_finish_modified    = 0
word_buffer             = []
recent_predictions      = deque(maxlen=VOTE_WINDOW)  # rolling window of last N signs


def write_topn(prediction_row, building_sign=None, building_count=0, confirmed=None):
    """Write top-5 predictions as JSON for the camera window to read."""
    scores = prediction_row.tolist()
    ranked = sorted(
        [{"sign": TARGET_SIGNS[i], "conf": round(scores[i], 4)} for i in range(len(scores))],
        key=lambda x: x["conf"], reverse=True
    )[:5]
    data = {
        "top5":      ranked,
        "building":  {"sign": building_sign, "count": building_count, "total": VOTE_NEEDED},
        "confirmed": confirmed,
    }
    with open(TOPN_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


while True:
    # ── Check finish gesture ──
    if os.path.exists(FINISH_PATH):
        finish_modified = os.path.getmtime(FINISH_PATH)
        if finish_modified > last_finish_modified:
            last_finish_modified = finish_modified

            if word_buffer:
                sentence = " ".join(word_buffer)
                en_buf   = [SIGN_EN.get(s, s) for s in word_buffer]
                print(f"\nFinish — sentence: {' > '.join(en_buf)}")
                with open(RESULT_PATH, "w", encoding="utf-8") as f:
                    f.write(f">> {sentence}")
                word_buffer = []
                recent_predictions.clear()
            else:
                print("Finish gesture — buffer empty")
                with open(RESULT_PATH, "w", encoding="utf-8") as f:
                    f.write("...")

    # ── Check new keypoints ──
    if os.path.exists(KEYPOINTS_PATH):
        modified = os.path.getmtime(KEYPOINTS_PATH)
        if modified > last_keypoints_modified:
            try:
                keypoints = np.load(KEYPOINTS_PATH)
            except (EOFError, ValueError, IOError):
                time.sleep(0.05)
                continue
            last_keypoints_modified = modified

            keypoints    = np.expand_dims(keypoints, axis=0)
            prediction   = model.predict(keypoints, verbose=0)
            predicted_idx = np.argmax(prediction)
            confidence   = prediction[0][predicted_idx]
            sign         = TARGET_SIGNS[predicted_idx]
            threshold    = SIGN_THRESHOLDS.get(sign, 0.80)
            en           = SIGN_EN.get(sign, sign)

            # Add to rolling window — always, including "none" and low confidence
            vote_entry = sign if (confidence >= threshold and sign != "none") else "none"
            recent_predictions.append(vote_entry)

            # Count how many of the window are the dominant non-none sign
            non_none = [s for s in recent_predictions if s != "none"]
            if non_none:
                top_sign  = max(set(non_none), key=non_none.count)
                top_count = non_none.count(top_sign)
            else:
                top_sign  = "none"
                top_count = 0

            win_size = len(recent_predictions)

            if top_count >= VOTE_NEEDED:
                # ── Confirmed ──
                recent_predictions.clear()   # reset window after confirmation
                conf_en = SIGN_EN.get(top_sign, top_sign)

                if not word_buffer or word_buffer[-1] != top_sign:
                    word_buffer.append(top_sign)
                    result = f"{top_sign} ({confidence:.0%})"
                    print(f"  CONFIRMED: {conf_en} ({confidence:.0%}) | buffer: {[SIGN_EN.get(s,s) for s in word_buffer]}")
                    with open(RESULT_PATH, "w", encoding="utf-8") as f:
                        f.write(result)
                    write_topn(prediction[0], confirmed=top_sign)
                else:
                    print(f"  dup: {conf_en}")
                    with open(RESULT_PATH, "w", encoding="utf-8") as f:
                        f.write(f"{top_sign} ({confidence:.0%}) [dup]")
                    write_topn(prediction[0], confirmed=top_sign)

            elif top_count > 0:
                # ── Building ──
                print(f"  building: {SIGN_EN.get(top_sign, top_sign)} ({confidence:.0%}) [{top_count}/{VOTE_NEEDED}]")
                with open(RESULT_PATH, "w", encoding="utf-8") as f:
                    f.write(f"? {top_sign} ({confidence:.0%}) [{top_count}/{VOTE_NEEDED}]")
                write_topn(prediction[0], building_sign=top_sign, building_count=top_count)

            else:
                # ── All none ──
                print(f"  {en} ({confidence:.0%}) — none")
                with open(RESULT_PATH, "w", encoding="utf-8") as f:
                    f.write("...")
                write_topn(prediction[0])

    time.sleep(0.1)
