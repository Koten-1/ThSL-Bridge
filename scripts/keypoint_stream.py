import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
from PIL import ImageFont, ImageDraw, Image
import time
import os
import json

TEMP_DIR = Path("D:/KachornThSL/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

COLLECT_FRAMES   = 30    # exactly 30 frames sent to model (matches training)
IDLE_WARMUP      = 3     # hands must appear for 3 frames before collecting starts
FINISH_THRESHOLD = 0.35  # wrist y-position to trigger finish gesture

FONT_PATH      = "D:/KachornThSL/assests/Sarabun-Regular.ttf"
KEYPOINTS_PATH = "D:/KachornThSL/temp/keypoints.npy"
TOPN_PATH      = "D:/KachornThSL/temp/topn.json"

try:
    font_large = ImageFont.truetype(FONT_PATH, 32)
    font_small = ImageFont.truetype(FONT_PATH, 22)
    thai_ok = True
except Exception as e:
    thai_ok = False
    print(f"Thai font not loaded: {e}")

def put_thai(frame, text, pos, font, color=(255, 255, 255)):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    ImageDraw.Draw(img).text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def draw_topn(frame, topn_data, font_small):
    """Draw estimation bars on the right side of the frame."""
    if not topn_data or "top5" not in topn_data:
        return frame

    h, w = frame.shape[:2]
    panel_w  = 210
    bar_h    = 18
    row_gap  = 30
    panel_x  = w - panel_w - 10
    start_y  = 90

    building  = topn_data.get("building", {})
    confirmed = topn_data.get("confirmed")

    # Semi-transparent dark panel background
    overlay = frame.copy()
    cv2.rectangle(overlay, (panel_x - 8, start_y - 8),
                  (w - 5, start_y + len(topn_data["top5"]) * row_gap + 10), (20, 20, 20), -1)
    frame = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)

    for i, item in enumerate(topn_data["top5"]):
        sign = item["sign"]
        conf = item["conf"]
        y    = start_y + i * row_gap

        # Bar fill colour: gold if confirmed, green if building, grey otherwise
        if confirmed and sign == confirmed:
            bar_col = (0, 215, 255)   # gold
        elif building.get("sign") == sign and building.get("count", 0) > 0:
            bar_col = (0, 200, 80)    # green — actively building
        else:
            bar_col = (120, 120, 120) # grey

        bar_len = int(conf * (panel_w - 70))
        cv2.rectangle(frame, (panel_x, y), (panel_x + bar_len, y + bar_h), bar_col, -1)
        cv2.rectangle(frame, (panel_x, y), (panel_x + panel_w - 70, y + bar_h), (180, 180, 180), 1)

        # Confidence % on the right of bar
        cv2.putText(frame, f"{conf:.0%}", (panel_x + panel_w - 62, y + bar_h - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 220, 220), 1)

        # Sign label (Thai needs PIL)
        if thai_ok and sign != "none":
            frame = put_thai(frame, sign, (panel_x, y - 2), font_small, (255, 255, 255))
        else:
            cv2.putText(frame, sign, (panel_x, y + bar_h - 3),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1)

    # Building counter dots
    if building.get("sign") and building.get("count", 0) > 0:
        count = building["count"]
        total = building.get("total", 4)
        dot_y = start_y + len(topn_data["top5"]) * row_gap + 8
        for d in range(total):
            col = (0, 200, 80) if d < count else (60, 60, 60)
            cv2.circle(frame, (panel_x + 10 + d * 18, dot_y), 6, col, -1)

    return frame


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5
)

cap = cv2.VideoCapture(1)
print("Webcam opened. Press Q to quit.")

# ── State machine ──
STATE_IDLE       = "IDLE"
STATE_COLLECTING = "COLLECTING"

state        = STATE_IDLE
idle_counter = 0          # counts consecutive frames with hands while IDLE
collected    = []         # frames gathered during COLLECTING

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results   = hands.process(frame_rgb)

    h, w = frame.shape[:2]

    lh = np.zeros(63)
    rh = np.zeros(63)
    lh_wrist_y = 1.0
    rh_wrist_y = 1.0

    hand_present = results.multi_hand_landmarks is not None

    if hand_present:
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks, results.multi_handedness
        ):
            coords = np.array([
                [lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark
            ]).flatten()
            label = handedness.classification[0].label
            if label == "Left":
                lh = coords
                lh_wrist_y = hand_landmarks.landmark[0].y
            else:
                rh = coords
                rh_wrist_y = hand_landmarks.landmark[0].y

        # Finish gesture — both wrists raised high
        if lh_wrist_y < FINISH_THRESHOLD and rh_wrist_y < FINISH_THRESHOLD:
            print("Finish gesture — signaling T2")
            with open("D:/KachornThSL/temp/finish.txt", "w", encoding="utf-8") as f:
                f.write("TRIGGER")
            state = STATE_IDLE
            idle_counter = 0
            collected = []
            time.sleep(1)
            continue

    keypoints_row = np.concatenate([lh, rh])  # 126 values per frame

    # ── State machine logic ──
    if state == STATE_IDLE:
        if hand_present:
            idle_counter += 1
            if idle_counter >= IDLE_WARMUP:
                state = STATE_COLLECTING
                collected = []
                print("Hands detected — collecting...")
        else:
            idle_counter = 0

    elif state == STATE_COLLECTING:
        collected.append(keypoints_row)

        if len(collected) == COLLECT_FRAMES:
            keypoints = np.array(collected)          # shape: (30, 126)
            np.save(KEYPOINTS_PATH, keypoints)
            print(f"Sent {COLLECT_FRAMES} frames to model")
            state = STATE_IDLE
            idle_counter = 0
            collected = []

    # ── Read result + top-N from predict_stream ──
    result_text = "..."
    if os.path.exists("D:/KachornThSL/temp/result.txt"):
        with open("D:/KachornThSL/temp/result.txt", "r", encoding="utf-8") as f:
            result_text = f.read()

    topn_data = None
    if os.path.exists(TOPN_PATH):
        try:
            with open(TOPN_PATH, "r", encoding="utf-8") as f:
                topn_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # ── UI ──
    cv2.rectangle(frame, (0, 0), (w, 75), (0, 0, 0), -1)
    cv2.rectangle(frame, (0, h - 80), (w, h), (0, 0, 0), -1)

    # Status indicator dot
    if state == STATE_IDLE:
        dot_color  = (0, 100, 255)   # orange — waiting
        state_text = "รอมือ" if thai_ok else "WAITING"
    else:
        dot_color  = (0, 255, 0)     # green — collecting
        progress   = len(collected)
        state_text = f"บันทึก {progress}/{COLLECT_FRAMES}" if thai_ok else f"REC {progress}/{COLLECT_FRAMES}"

    cv2.circle(frame, (w - 30, 38), 12, dot_color, -1)

    if thai_ok:
        frame = put_thai(frame, state_text,             (10,  8), font_small, (255, 255, 255))
        frame = put_thai(frame, f"ผลลัพธ์: {result_text}", (10, h - 73), font_large, (0, 255, 255))
        frame = put_thai(frame, "ยกมือทั้งสองข้าง = จบประโยค", (10, h - 38), font_small, (180, 180, 180))
    else:
        cv2.putText(frame, state_text,
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 1)
        cv2.putText(frame, f"Result: {result_text}",
                    (10, h - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Raise both hands = DONE",
                    (10, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

    # ── Estimation bars ──
    if topn_data and thai_ok:
        frame = draw_topn(frame, topn_data, font_small)
    elif topn_data:
        frame = draw_topn(frame, topn_data, None)

    cv2.imshow("ThSL Bridge", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
