# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""What the data looks like: the SAME word by two signers as hand skeletons (drawn from the saved keypoints, no video,
no faces), plus the 30 x 126 numbers the model really receives.
  python3 scripts/make_data_look.py ROOT OUT.png [WORD]     ROOT = folder with <signer>/<word>/*.npy (e.g. ~/Downloads/ThSL_keypoints/all28)
"""
import sys, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

for fam in ("TH Sarabun New", "Thonburi"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam; break
plt.rcParams["axes.unicode_minus"] = False
EDGES = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
INK, MUTED, BLUE, ORANGE, GREEN = "#1F2937", "#4B5563", "#2B5F8E", "#E08A2E", "#2E7D5B"
root, out = os.path.expanduser(sys.argv[1]), sys.argv[2]
word = sys.argv[3] if len(sys.argv) > 3 else "ขอบคุณ"
signers = ["S01", "S03"]
frames = [0, 6, 12, 18, 24, 29]
arrs = {s: np.load(sorted(glob.glob(f"{root}/{s}/{word}/*.npy"))[0]).astype(float) for s in signers}

def bbox(a):
    pts = np.concatenate([a[:, k * 63:(k + 1) * 63].reshape(-1, 21, 3)[:, :, :2].reshape(-1, 2) for k in (0, 1)])
    pts = pts[np.abs(pts).sum(1) > 0]
    return pts.min(0), pts.max(0)
bb = {s_: bbox(arrs[s_]) for s_ in signers}
HALF = max((hi - lo).max() for lo, hi in bb.values()) / 2 + 0.03

fig = plt.figure(figsize=(13, 5.6), dpi=200, facecolor="white")
gs = fig.add_gridspec(2, 6, left=0.07, right=0.55, top=0.82, bottom=0.16, wspace=0.08, hspace=0.12)
for r, s in enumerate(signers):
    a = arrs[s]
    for c, f in enumerate(frames):
        ax = fig.add_subplot(gs[r, c]); ctr = (bb[s][0] + bb[s][1]) / 2
        ax.set_xlim(ctr[0] - HALF, ctr[0] + HALF); ax.set_ylim(ctr[1] + HALF, ctr[1] - HALF); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color("#C7CDD6")
        for slot, col in ((0, BLUE), (1, ORANGE)):
            h = a[f, slot * 63:(slot + 1) * 63].reshape(21, 3)
            if not h.any(): continue
            for i, j in EDGES: ax.plot([h[i, 0], h[j, 0]], [h[i, 1], h[j, 1]], color=col, lw=1.6)
            ax.scatter(h[:, 0], h[:, 1], s=9, color=col, zorder=3)
        if r == 0: ax.set_title(f"เฟรม {f + 1}", fontsize=12, color=MUTED)
        if c == 0: ax.set_ylabel(s, fontsize=15, color=INK, rotation=0, labelpad=22, va="center", fontweight="bold")
fig.text(0.07, 0.93, f"คำเดียวกัน ({word}) จากผู้แสดงสองคน", fontsize=17, color=INK, fontweight="bold")
fig.text(0.07, 0.03, "วาดจากตัวเลขจุดมือที่เก็บไว้ ไม่ใช่ภาพวิดีโอ · สีฟ้าและสีส้มคือมือสองช่องของ MediaPipe · ขยายภาพให้เห็นมือของแต่ละคน", fontsize=11, color=MUTED)
# heatmap of the real array
ax = fig.add_axes([0.62, 0.2, 0.36, 0.62])
a = arrs["S01"]
ax.imshow(a, aspect="auto", cmap="viridis", interpolation="nearest")
ax.axvline(62.5, color="white", lw=1.5)
ax.set_xticks([31, 94]); ax.set_xticklabels(["ช่องมือที่ 1\n(63 ค่า)", "ช่องมือที่ 2\n(63 ค่า)"], fontsize=11)
ax.set_yticks([0, 9, 19, 29]); ax.set_yticklabels(["1", "10", "20", "30"], fontsize=11)
ax.set_ylabel("เฟรม (30 เฟรม)", fontsize=12)
ax.set_title("ตัวเลขที่โมเดลเห็นจริง (S01): 30 × 126", fontsize=15, color=INK, loc="left", fontweight="bold")
fig.text(0.62, 0.03, "แถวสีเรียบ = ไม่พบมือในเฟรมนั้น (เป็นศูนย์)", fontsize=11, color=MUTED)
fig.savefig(out, facecolor="white"); print("saved", out)
