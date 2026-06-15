"""
Step 1 of 2 — run with: thsl_env (has cv2 + mediapipe, no tensorflow)
Re-extracts keypoints from raw videos and saves them to temp/inspect/
Then run inspect_sign_infer.py with thsl_tf_env to see model predictions.

Usage: python scripts/inspect_sign.py ช่วย
"""
import sys, os, cv2, numpy as np, mediapipe as mp
from pathlib import Path

SIGN = sys.argv[1] if len(sys.argv) > 1 else "ช่วย"
RAW_DIR  = Path(f"D:/KachornThSL/data/raw/{SIGN}")
PROC_DIR = Path(f"D:/KachornThSL/data/processed/{SIGN}")
OUT_DIR  = Path(f"D:/KachornThSL/temp/inspect/{SIGN}")
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLLECT_FRAMES = 30
mp_hands = mp.solutions.hands
detector = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

def extract(video_path):
    cap = cv2.VideoCapture(str(video_path))
    frames, hand_count = [], 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        res = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        lh = rh = np.zeros(63)
        if res.multi_hand_landmarks:
            hand_count += 1
            for lm, hd in zip(res.multi_hand_landmarks, res.multi_handedness):
                coords = np.array([[p.x, p.y, p.z] for p in lm.landmark]).flatten()
                if hd.classification[0].label == "Left":
                    lh = coords
                else:
                    rh = coords
        frames.append(np.concatenate([lh, rh]))
    cap.release()
    n = len(frames)
    if n == 0:
        return None, 0, 0
    idx = np.linspace(0, n - 1, COLLECT_FRAMES, dtype=int)
    return np.array([frames[i] for i in idx]), hand_count, n

print(f"\nExtracting keypoints for: {SIGN}")
print(f"Raw videos found: {len(list(RAW_DIR.glob('*.mp4')))}\n")

for mp4 in sorted(RAW_DIR.glob("*.mp4")):
    kp, hand_frames, total_frames = extract(mp4)
    hand_pct = hand_frames / max(total_frames, 1) * 100
    saved_npy = PROC_DIR / (mp4.stem + ".npy")

    print(f"{mp4.name}")
    print(f"  {total_frames} frames total, hands in {hand_frames} ({hand_pct:.0f}%)", end="")

    if kp is None:
        print(" — FAILED to read video")
        continue

    # Save freshly extracted keypoints
    out_path = OUT_DIR / f"live_{mp4.stem}.npy"
    np.save(out_path, kp)

    # Compare with saved .npy if it exists
    if saved_npy.exists():
        saved = np.load(saved_npy)
        diff = np.abs(kp - saved).max()
        zero_frames_live  = int(np.all(kp.reshape(30, 126) == 0, axis=1).sum())
        zero_frames_saved = int(np.all(saved.reshape(30, 126) == 0, axis=1).sum())
        print(f"\n  Max diff vs saved .npy: {diff:.6f}  {'(match)' if diff < 1e-4 else '(DIFFERENT)'}")
        print(f"  Zero-hand frames — live: {zero_frames_live}/30  |  saved: {zero_frames_saved}/30")
    else:
        print(f"\n  No saved .npy found at {saved_npy}")
    print()

print(f"Saved re-extracted .npy files to: {OUT_DIR}")
print("Now run: python scripts/inspect_sign_infer.py to see model predictions")
