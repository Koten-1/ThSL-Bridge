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

VIDEO_EXTS = {".mp4", ".mov"}

# Flat classes: RAW_DIR/<sign>/*.{mp4,mov} — no signer subfolder (shared across signers)
FLAT_SIGN_DIRS = {"finish", "none"}

# Signer-nested: RAW_DIR/<signer_folder>/<sign>/*.{mp4,mov}
# (ปอป่าน ตัดแยก excluded — incomplete vocabulary coverage)
SIGNER_FOLDERS = {
    "กร": "กร",
    "ตะวัน": "ตะวัน",
    "ปิ่น ตัดแยก": "ปิ่น",
    "อัยด้า_ตัดแยก": "อัยด้า",
}

SIGNER_SUFFIXES = ["_ตะวัน", "_ปิ่น", "_อัยด้า", "_ไอด้า", "_กร"]


def strip_signer_suffix(word):
    for suffix in SIGNER_SUFFIXES:
        if word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def list_videos(folder):
    return sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTS)


def process_video(video_path, out_path):
    if out_path.exists():
        print(f"  [skip] {video_path.name}")
        return

    print(f"  [process] {video_path.name}")

    cap = cv2.VideoCapture(str(video_path))
    frames_keypoints = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Only keep frames where at least one hand is detected
        # This matches the live pipeline which collects only during hand presence
        if results.multi_hand_landmarks:
            lh = np.zeros(63)
            rh = np.zeros(63)
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                coords = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
                if handedness.classification[0].label == "Left":
                    lh = coords
                else:
                    rh = coords
            frames_keypoints.append(np.concatenate([lh, rh]))

    cap.release()

    MIN_HAND_FRAMES = 15
    if len(frames_keypoints) < MIN_HAND_FRAMES:
        print(f"    [skip] only {len(frames_keypoints)} hand frames — bad recording, need at least {MIN_HAND_FRAMES}")
        return

    arr = np.array(frames_keypoints)

    NUM_FRAMES = 30
    indices = np.linspace(0, len(arr) - 1, NUM_FRAMES, dtype=int)
    arr = arr[indices]  # shape: (30, 126)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(out_path), arr)
    print(f"    saved: {arr.shape}  ({len(frames_keypoints)} hand frames → resampled to 30)")


# 1) flat classes (finish, none) — no signer subfolder
for sign_name in FLAT_SIGN_DIRS:
    sign_dir = RAW_DIR / sign_name
    if not sign_dir.is_dir():
        continue
    videos = list_videos(sign_dir)
    print(f"{sign_name}: {len(videos)} videos")
    for video_path in videos:
        out_path = PROCESSED_DIR / sign_name / (video_path.stem + ".npy")
        process_video(video_path, out_path)

# 2) signer-nested classes
for folder_name, signer in SIGNER_FOLDERS.items():
    signer_dir = RAW_DIR / folder_name
    if not signer_dir.is_dir():
        print(f"[skip] missing signer dir: {folder_name}")
        continue
    for word_dir in sorted(signer_dir.iterdir()):
        if not word_dir.is_dir():
            continue
        sign_name = strip_signer_suffix(word_dir.name)
        videos = list_videos(word_dir)
        print(f"{signer}/{sign_name}: {len(videos)} videos")
        for video_path in videos:
            out_path = PROCESSED_DIR / sign_name / (video_path.stem + ".npy")
            process_video(video_path, out_path)