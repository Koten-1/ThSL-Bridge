import cv2, os, numpy as np

video_path = r"D:\KachornThSL\reference video\What if AI could bridge the gap between sign language and spoken EnglishThis prototype uses Medi (1).mp4"
out_dir    = r"D:\KachornThSL\reference video\frames"
os.makedirs(out_dir, exist_ok=True)

cap   = cv2.VideoCapture(video_path)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps   = cap.get(cv2.CAP_PROP_FPS)
dur   = total / fps if fps > 0 else 0
print(f"Total frames: {total}, FPS: {fps:.1f}, Duration: {dur:.1f}s")

for i, fn in enumerate(np.linspace(0, total - 1, 16, dtype=int)):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(fn))
    ret, frame = cap.read()
    if ret:
        path = f"{out_dir}\\frame_{i:02d}_at_{fn}.jpg"
        cv2.imwrite(path, frame)
        print(f"Saved frame {i} @ {fn}")

cap.release()
print("Done.")
