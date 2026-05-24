import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
import time
import os

TEMP_DIR = Path("D:/KachornThSL/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

NUM_FRAMES = 30

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5
)

cap = cv2.VideoCapture(1)
print("Webcam opened. Press Q to quit.")

while True:
    frames_keypoints = []

    for _ in range(NUM_FRAMES):
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            lh = np.zeros(63)
            rh = np.zeros(63)
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                coords = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
                if handedness.classification[0].label == "Left":
                    lh = coords
                else:
                    rh = coords
            # draw landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            lh = np.zeros(63)
            rh = np.zeros(63)

        frames_keypoints.append(np.concatenate([lh, rh]))

        # UI overlay
        result_path = "D:/KachornThSL/temp/result.txt"
        result_text = "..."
        if os.path.exists(result_path):
            with open(result_path, "r", encoding="utf-8") as f:
                result_text = f.read()

        status = "Collecting..." if len(frames_keypoints) < NUM_FRAMES else "Processing..."
        cv2.rectangle(frame, (0, 0), (640, 60), (0, 0, 0), -1)
        cv2.putText(frame, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, result_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Signing", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    arr = np.array(frames_keypoints)
    if len(arr) == NUM_FRAMES:
        non_zero_frames = np.sum(np.any(arr != 0, axis=1))
        if non_zero_frames >= 15:
            np.save("D:/KachornThSL/temp/keypoints.npy", arr)
            print(f"Keypoints saved. ({non_zero_frames} frames with hands)")
        else:
            print("No hands detected - skipping")
        time.sleep(1)

cap.release()
cv2.destroyAllWindows()
