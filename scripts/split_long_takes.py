#!/usr/bin/env python3
"""Split long-take recordings into one keypoint file per repetition.

A volunteer records one video per word and repeats the sign about 10 times,
lowering their hands in between. This finds each repetition, cuts it the same way
the live web app would (start when the hand rises, stop after it goes still), and
saves a (30, 126) keypoint array per repetition, the exact input the LSTM expects.

Keypoints only: no video is re-saved unless --save-clips is given, which fits the
"no faces in the dataset" promise in the consent form.

Input files are named   <signer>_<word>_take<NN>.mp4     e.g.  S01_ปวดท้อง_take03.mp4
Output files are named  <signer>_<word>_t<NN>r<KK>.npy   e.g.  S01_ปวดท้อง_t03r07.npy

Usage:
  python3 scripts/split_long_takes.py TAKES_DIR --out DATA_DIR [--expected 10] [--save-clips]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

# Same numbers as innovation/web_app/index.html, so training clips look like live segments.
STILL_THRESHOLD = 0.03   # mean abs change between frames below this counts as "still"
LEAD_MS = 133            # keep this much before the first movement (app: IDLE_WARMUP_MS)
TAIL_MS = 200            # keep this much after the last movement (app: STILL_MS)
MIN_HAND_FRAMES = 15     # same rule as scripts/extract_keypoints.py
NUM_FRAMES = 30

NAME_RE = re.compile(r"^(?P<signer>[^_]+)_(?P<word>.+)_take(?P<take>\d+)$")
VIDEO_EXTS = {".mp4", ".mov", ".m4v"}


def frame_row(result):
    """126 numbers (left hand 63 + right hand 63), mirroring extract_keypoints.py.
    Returns (row, lowest_y_of_highest_landmark) or (None, None) if no hand."""
    if not result.multi_hand_landmarks:
        return None, None
    lh, rh = np.zeros(63), np.zeros(63)
    top_y = 1.0
    for hand, handed in zip(result.multi_hand_landmarks, result.multi_handedness):
        pts = np.array([[lm.x, lm.y, lm.z] for lm in hand.landmark])
        top_y = min(top_y, float(pts[:, 1].min()))
        if handed.classification[0].label == "Left":
            lh = pts.flatten()
        else:
            rh = pts.flatten()
    return np.concatenate([lh, rh]), top_y


def scan_video(path, max_side):
    """One pass over the video. Returns fps, rows (n,126), present (n,), top_y (n,)."""
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2,
                                     min_detection_confidence=0.5)
    rows, present, top = [], [], []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        h, w = frame.shape[:2]
        scale = max_side / max(h, w)
        if scale < 1:   # 4K frames are slow and add nothing: landmarks are normalized anyway
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
        res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        row, top_y = frame_row(res)
        present.append(row is not None)
        rows.append(row if row is not None else np.zeros(126))
        top.append(top_y if top_y is not None else 1.0)
    cap.release()
    hands.close()
    return fps, np.array(rows), np.array(present, dtype=bool), np.array(top)


def find_runs(active, max_gap):
    """Contiguous runs of True, merging runs separated by <= max_gap False frames."""
    runs, start, last = [], None, None
    for i, a in enumerate(active):
        if a:
            if start is None:
                start = i
            elif i - last - 1 > max_gap:
                runs.append((start, last))
                start = i
            last = i
    if start is not None:
        runs.append((start, last))
    return runs


def trim_still(kp, fps):
    """Drop the held pose before the first movement and after the last one,
    leaving the same lead/tail the live app would have."""
    if len(kp) < 3:
        return kp
    delta = np.abs(np.diff(kp, axis=0)).mean(axis=1)
    moving = np.where(delta >= STILL_THRESHOLD)[0]
    if len(moving) == 0:   # a static handshape: keep a short stretch from the middle
        keep = min(len(kp), int(fps))
        mid = len(kp) // 2
        return kp[max(0, mid - keep // 2): mid + keep // 2 + 1]
    lead = int(round(LEAD_MS / 1000 * fps))
    tail = int(round(TAIL_MS / 1000 * fps))
    return kp[max(0, moving[0] - lead): min(len(kp), moving[-1] + 1 + tail)]


def resample(kp):
    idx = np.linspace(0, len(kp) - 1, NUM_FRAMES, dtype=int)
    return kp[idx].astype(np.float32)


def write_clip(src, dst, fps, ranges, max_side):
    """Optional: save the repetitions as short mp4 files for a human to review."""
    cap = cv2.VideoCapture(str(src))
    writers, i = {}, 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        for k, (a, b) in enumerate(ranges):
            if a <= i <= b:
                h, w = frame.shape[:2]
                s = min(1.0, max_side / max(h, w))
                f = cv2.resize(frame, (int(w * s), int(h * s))) if s < 1 else frame
                if k not in writers:
                    writers[k] = cv2.VideoWriter(str(dst(k)), cv2.VideoWriter_fourcc(*"mp4v"),
                                                 fps, (f.shape[1], f.shape[0]))
                writers[k].write(f)
        i += 1
    cap.release()
    for w in writers.values():
        w.release()


def process_take(path, signer, word, take, out_dir, args):
    fps, rows, present, top_y = scan_video(path, args.max_side)
    # a frame is "active" when a hand is visible and raised above the rest band
    active = present & (top_y < args.rest_y)
    runs = find_runs(active, max_gap=int(round(args.gap_s * fps)))

    word_dir = Path(out_dir) / signer / word
    word_dir.mkdir(parents=True, exist_ok=True)
    kept, notes, clip_ranges = 0, [], []
    for a, b in runs:
        dur = (b - a + 1) / fps
        if dur < args.min_len or dur > args.max_len:
            notes.append(f"skipped run of {dur:.1f}s")
            continue
        kp = rows[a:b + 1][present[a:b + 1]]       # only frames with a detected hand, like extract_keypoints
        if len(kp) < MIN_HAND_FRAMES:
            notes.append(f"skipped run with {len(kp)} hand frames")
            continue
        kept += 1
        np.save(word_dir / f"{signer}_{word}_t{take:02d}r{kept:02d}.npy", resample(trim_still(kp, fps)))
        clip_ranges.append((a, b))

    if args.save_clips and clip_ranges:
        clip_dir = Path(out_dir) / "_clips" / signer / word
        clip_dir.mkdir(parents=True, exist_ok=True)
        write_clip(path, lambda k: clip_dir / f"{signer}_{word}_t{take:02d}r{k + 1:02d}.mp4",
                   fps, clip_ranges, args.max_side)

    status = "ok" if kept == args.expected else ("too_few" if kept < args.expected else "too_many")
    return {"file": path.name, "signer": signer, "word": word, "take": take, "fps": round(fps, 1),
            "frames": len(rows), "runs_found": len(runs), "kept": kept,
            "expected": args.expected, "status": status, "notes": "; ".join(notes)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("takes", help="a long-take video, or a folder of them")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--expected", type=int, default=10, help="repetitions per take")
    ap.add_argument("--vocab", default=str(Path(__file__).parent / "vocab.json"))
    ap.add_argument("--rest-y", type=float, default=0.85,
                    help="hands whose highest point is below this (0 top, 1 bottom) count as resting")
    ap.add_argument("--gap-s", type=float, default=0.3, help="merge detections split by a gap this short")
    ap.add_argument("--min-len", type=float, default=0.5)
    ap.add_argument("--max-len", type=float, default=6.0)
    ap.add_argument("--max-side", type=int, default=960, help="shrink frames to this size before tracking")
    ap.add_argument("--save-clips", action="store_true", help="also write each repetition as a short mp4")
    args = ap.parse_args()

    src = Path(args.takes)
    files = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.suffix.lower() in VIDEO_EXTS)
    vocab = set()
    try:
        vocab = {w["th"] for w in json.loads(Path(args.vocab).read_text(encoding="utf-8"))["words"]}
    except Exception:
        print(f"note: could not read vocab file {args.vocab}, word names are not checked")

    report, skipped = [], []
    for p in files:
        m = NAME_RE.match(p.stem)
        if not m:
            skipped.append(p.name)
            continue
        signer, word, take = m["signer"], m["word"], int(m["take"])
        print(f"{p.name} ...", flush=True)
        row = process_take(p, signer, word, take, args.out, args)
        if vocab and word not in vocab:
            row["notes"] = (row["notes"] + "; " if row["notes"] else "") + "word not in vocab.json"
        report.append(row)
        print(f"   {row['kept']}/{args.expected} repetitions ({row['status']}) {row['notes']}")

    if report:
        out_csv = Path(args.out) / "split_report.csv"
        with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(report[0].keys()))
            w.writeheader()
            w.writerows(report)
        bad = [r for r in report if r["status"] != "ok" or "vocab" in r["notes"]]
        print(f"\n{len(report)} takes, {sum(r['kept'] for r in report)} repetitions saved. "
              f"{len(bad)} take(s) need a human look:")
        for r in bad:
            print(f"  {r['file']}: {r['kept']}/{r['expected']} {r['notes']}")
        print(f"report: {out_csv}")
    if skipped:
        print(f"\nignored (name does not match signer_word_takeNN): {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
