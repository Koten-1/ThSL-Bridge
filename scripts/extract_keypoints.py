import mediapipe as mp
import cv2
import numpy as np
from pathlib import Path

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5
)

RAW_DIR = Path("D:/KachornThSL/data/raw")
PROCESSED_DIR = Path("D:/KachornThSL/data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

signs = [f for f in RAW_DIR.iterdir() if f.is_dir()]

for sign_dir in signs:
    sign_name = sign_dir.name
    videos = list(sign_dir.glob("*.mp4"))
    print(f"{sign_name}: {len(videos)} videos")

    for video_path in videos:
        out_path = PROCESSED_DIR / sign_name / (video_path.stem + ".npy")

        if out_path.exists():
            print(f"  [skip] {video_path.name}")
            continue

        print(f"  [process] {video_path.name}")

        cap = cv2.VideoCapture(str(video_path))
        frames_keypoints = []

        while True:
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
            else:
                lh = np.zeros(63)
                rh = np.zeros(63)

            frames_keypoints.append(np.concatenate([lh, rh]))

        cap.release()
        
        arr = np.array(frames_keypoints)  


        NUM_FRAMES = 30
        indices = np.linspace(0, len(arr) - 1, NUM_FRAMES, dtype=int)
        arr = arr[indices]  # shape: (30, 126)


        out_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(str(out_path), arr)
        print(f"    saved: {arr.shape}")
        print(f"    frames: {len(frames_keypoints)}")