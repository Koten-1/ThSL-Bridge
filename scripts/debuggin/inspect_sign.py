#จะรู้ไดไงละ ว่า keypoint ที่ได้จาก raw video แล้วมา processed มันใช้ได้จริงหรือเปล่า เราเลยต้องมาดูเนื้อใน
"""
Step 1 of 2 — run with: thsl_env (has cv2 + mediapipe, no tensorflow)
Re-extracts keypoints from raw videos and saves them to temp/inspect/
Then run inspect_sign_infer.py with thsl_tf_env to see model predictions.

Usage: python scripts/inspect_sign.py ช่วย
"""
import sys, os, cv2, numpy as np, mediapipe as mp
from pathlib import Path

SIGN = sys.argv[1] if len(sys.argv) > 1 else "ช่วย"
RAW_DIR  = Path(f"D:/KachornThSL/data/raw/{SIGN}") #ต้นฉบับ
PROC_DIR = Path(f"D:/KachornThSL/data/processed/{SIGN}") #อันนี้ที่สะกัดมาแล้ว ซึ่งเราจะมาดูเนื้อหากัน
OUT_DIR  = Path(f"D:/KachornThSL/temp/inspect/{SIGN}") #เอาไว้ลบง่ายๆ
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLLECT_FRAMES = 30 #จำนวนเฟรมที่เราจะเก็บ keypoint ต่อวิดิโอ ถ้าคลิปมัน 90 วิ ก็คัดมาแค่ 3,6,9..,90 หรือช่วงหาร 3 นั้นเอง
mp_hands = mp.solutions.hands
detector = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

def extract(video_path): #re-extract keypoint จาก rawที่มีอยู่แล้วเอามาเทียบกับ กลุ่ม processed ว่า
    cap = cv2.VideoCapture(str(video_path)) 
    frames, hand_count = [], 0 #กี่เฟรมที่เห็นมือ 
    while True:
        ret, frame = cap.read() #อ่านวิดิโอที่ละเฟรม ถ้าอ่านได้ ret จะเป็น True แล้วตัวแปร frame จะมีข้อมูลภาพของเฟรมนั้นๆ แต่ถ้าอ่านไม่ได้ ret จะเป็น False ซึ่งหมายความว่าเราอาจจะถึงจุดสิ้นสุดของวิดิโอแล้ว หรือเกิดข้อผิดพลาดในการอ่านวิดิโอ
        if not ret:
            break
        res = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) #mediapipe ใช้ภาพแบบ RGB แต่ OpenCV อ่านมาเป็น BGR เราต้องแปลงก่อนถึงจะส่งให้ mediapipe ตรวจจับมือได้ถูกต้อง,ส่วน detector.process() จะทำการตรวจจับมือในภาพที่ส่งเข้าไป และคืนผลลัพธ์เป็นวัตถุที่มีข้อมูลเกี่ยวกับมือที่พบในภาพนั้นๆ ซึ่งเราสามารถนำข้อมูลนี้ไปใช้ในการวิเคราะห์ต่อไปได้
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

# มาดูละเอียดที่ไฟล์นี้
#1 ทำไมมันถึงบอกได้ว่า คลิปที่ scrape มา มันไม่ work ละ hand_pct = hand_count / total_frames * 100 คือจุดที่บอกว่าการตรวจจับมือจากคลิปมีมากน้อยแค่ไหน แล้วทำเป็น % ยิ่งน้อย ยิ่งใช้ไม่ได้ เพราะ model มันต้องการ keypoint ที่มีมืออยู่เท่านั้นถึงจะเดาคำได้ถูกต้อง ซึ่งถ้า % มันน้อยมากๆ แปลว่าในคลิปนั้นๆ มันอาจจะมีช่วงที่ไม่มีมือ หรือมือไม่ชัดเจนเยอะเกินไป ทำให้การเดาคำมันผิดพลาดได้ง่ายนั่นเอง
#2 ที่สำคัญคือวิธีการดึง keypoint ที่ใช้จริงอัันนี้มันเป็นฉบับที่ดึง 30 frame ตั้งแต่ที่เจอมือแบบทื่อๆ ผมเลยมาเช็คว่าการที่มันเก็บเฟรมที่ไม่มีมือมีผลต่อการเดาคำไหม ซึ่งคำตอบคือใช้ ถ้าดูที่
#ช่วย:  saved 10/11 correct   (clean data — what training looked like)
#ช่วย:  live   4/11 correct   (zero-data — what live was sending)
#ที่เห็นคือการเก็บเฟรมของจริงคืออัน live(ของเก่านะ) มันมีgap จากที่extract_keypojnt อ่านมาเยอะมาก(อันที่saved) นี้เลยเป็นหนึ่งในตัวชี้วัดว่าก่อนหน้านี้ การอ่านแบบก่อนถึงใช้ไม่ได้
# also what's out of 11 ?mean? out of 11 frame?