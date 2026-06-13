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
import threading
from collections import deque
import postprocess   # Typhoon LLM + gTTS (same scripts/ dir)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

TARGET_SIGNS = [
    "คนหูหนวก", "คุณ", "ช่วย", "ขอบคุณ",
    "ฉัน", "ต้องการ", "เข้าใจ", "ไม่", "ถาม", "บอก", "finish", "none"
]

# English labels for terminal display (PowerShell can't show Thai)
SIGN_EN = {
    "คนหูหนวก": "deaf",
    "คุณ":      "you",
    "ช่วย":     "help",
    "ขอบคุณ":   "thank-you",
    "ฉัน":      "I/me",
    "ต้องการ":  "want",
    "เข้าใจ":   "understand",
    "ไม่":      "no/not",
    "ถาม":      "ask",
    "บอก":      "tell",
    "finish":   "finish",
    "none":     "none",
}

SIGN_THRESHOLDS = {
    # correct=0.96, wrong=0.00 → safe low threshold
    "คนหูหนวก": 0.70,
    # correct=0.69, wrong=0.71 → BROKEN (wrong > correct), set below correct_conf
    "คุณ":      0.60,
    # correct=0.80, wrong=0.91 → BROKEN (wrong > correct), threshold can't fix this
    "ช่วย":     0.65,
    # correct=1.00, wrong=0.00 → perfect
    "ขอบคุณ":   0.80,
    # correct=0.88, wrong=0.59 → decent gap
    "ฉัน":      0.75,
    # correct=0.85, wrong=0.70 → OK gap
    "ต้องการ":  0.78,
    # correct=0.94, wrong=0.77 → good gap
    "เข้าใจ":   0.85,
    # correct=0.75, wrong=0.00 → FIXED (was broken before retrain)
    "ไม่":      0.65,
    # correct=0.74, wrong=0.69 → tiny gap (0.05), marginal
    "ถาม":      0.70,
    # NEW sign — placeholder, recalibrate with check_thresholds.py after retrain
    "บอก":      0.75,
    # NEW finish class — triggers sentence output, recalibrate after retrain
    "finish":   0.70,
    # none is never confirmed as a word — threshold doesn't matter in practice
    "none":     0.80,
}

VOTE_WINDOW = 3   # look at last N predictions
VOTE_NEEDED = 1   # one confident prediction confirms — keypoint_stream now sends one
                  # complete sign per gesture, so multi-vote agreement is unnecessary
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
    Dense(12, activation='softmax')
])

model.load_weights("D:/KachornThSL/models/thsl_model_v6c.weights.h5")
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
                # Typhoon → natural sentence → gTTS speech (background, non-blocking)
                threading.Thread(target=postprocess.process,
                                 args=(list(word_buffer),), daemon=True).start()
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

                # ── "finish" is a learned class: end the sentence, don't add as a word ──
                if top_sign == "finish":
                    if word_buffer:
                        sentence = " ".join(word_buffer)
                        en_buf   = [SIGN_EN.get(s, s) for s in word_buffer]
                        print(f"\nFinish (sign) — sentence: {' > '.join(en_buf)}")
                        with open(RESULT_PATH, "w", encoding="utf-8") as f:
                            f.write(f">> {sentence}")
                        # Typhoon → natural sentence → gTTS speech (background)
                        threading.Thread(target=postprocess.process,
                                         args=(list(word_buffer),), daemon=True).start()
                        word_buffer = []
                    else:
                        print("Finish (sign) — buffer empty")
                        with open(RESULT_PATH, "w", encoding="utf-8") as f:
                            f.write("...")
                    write_topn(prediction[0], confirmed=top_sign)

                elif not word_buffer or word_buffer[-1] != top_sign:
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
