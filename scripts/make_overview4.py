# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Four-step system overview with pictures (sign -> word). Hands are drawn from real saved keypoints (no photos).
  python3 scripts/make_overview4.py KEYPOINT_ROOT OUT_DIR
Writes fig24_overview4_th.png and fig24_overview4_en.png
"""
import sys, os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrow

EDGES = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
STEPCOL = ["#F0953A", "#3DA35D", "#7B4FD6", "#E0559E"]
INK, MUTED, BL, BLF, PUR, PURF, GREEN = "#1F2937", "#4B5563", "#2B5F8E", "#E3ECF6", "#6B4E9B", "#EDE7F6", "#2E7D5B"
root, out = os.path.expanduser(sys.argv[1]), sys.argv[2]
A = np.load(sorted(glob.glob(f"{root}/S01/ขอบคุณ/*.npy"))[0]).astype(float)
FR = int(np.argmax([(A[i, :63].any() and A[i, 63:].any()) * 1.0 + np.abs(A[i]).sum() * 1e-6 for i in range(30)]))

TXT = {
 "th": dict(font="TH Sarabun New", title="ภาพรวมระบบ: จากภาษามือเป็นคำ", sub="ภาพจากกล้องถูกประมวลผลในเครื่องผู้ใช้",
            t=["ผู้ใช้ทำท่า", "อ่านมือเป็นตัวเลข", "LSTM จำแนกคำ", "ตอบหรือไม่แน่ใจ"],
            c=["ทำท่าหน้ากล้อง\nเว็บแคมหรือมือถือ", "MediaPipe หา 21 จุดต่อมือ\n= 126 ค่าต่อเฟรม ตัดท่าแล้ว\nย่อเหลือ 30 เฟรม",
               "อ่าน 30 เฟรมต่อกัน\nแล้วให้คะแนนแต่ละคำ", "ถึงเกณฑ์: แสดงคำ\nไม่ถึง: บอกว่า \"ไม่แน่ใจ\""],
            frames="30 เฟรม", vals="126 ค่า", word="ขอบคุณ", unsure="ไม่แน่ใจ", ok="ถึงเกณฑ์", no="ไม่ถึงเกณฑ์", orr="หรือ", tick="เกณฑ์", fs=1.0),
 "en": dict(font="Helvetica", title="System overview: from sign to word", sub="Camera images are processed on the user's device",
            t=["User signs", "Read hands as numbers", "LSTM classifies", "Answer or \"not sure\""],
            c=["Signs in front of\na webcam or phone", "MediaPipe finds 21 points per hand\n= 126 values per frame; the sign is cut\nand resampled to 30 frames",
               "Reads the 30 frames in order\nand scores each word", "Reaches the threshold: show the word\nBelow it: say \"not sure\""],
            frames="30 frames", vals="126 values", word="thank you", unsure="not sure", ok="above threshold", no="below threshold", orr="or", tick="threshold", fs=0.82),
}

def skel(ax, fr, x0, y0, w, h, lw=1.4):
    pts = []
    for slot, col in ((0, BL), (1, "#E08A2E")):
        hnd = fr[slot * 63:(slot + 1) * 63].reshape(21, 3)
        if hnd.any(): pts.append((hnd[:, :2], col))
    allp = np.concatenate([p for p, _ in pts]); lo, hi = allp.min(0), allp.max(0)
    sc = min(w / (hi[0] - lo[0] + 1e-6), h / (hi[1] - lo[1] + 1e-6)) * 0.86
    cx, cy = (lo + hi) / 2
    T = lambda p: np.c_[x0 + w / 2 + (p[:, 0] - cx) * sc, y0 + h / 2 - (p[:, 1] - cy) * sc]
    for p, col in pts:
        q = T(p)
        for i, j in EDGES: ax.plot([q[i, 0], q[j, 0]], [q[i, 1], q[j, 1]], color=col, lw=lw, zorder=5)
        ax.scatter(q[:, 0], q[:, 1], s=7, color=col, zorder=6)

def make(lang):
    T = TXT[lang]; plt.rcParams["font.family"] = T["font"]; k = T["fs"]
    fig, ax = plt.subplots(figsize=(12.5, 5.0), dpi=200, facecolor="white")
    ax.set_xlim(0, 24.5); ax.set_ylim(0, 9.8); ax.axis("off")
    ax.text(0, 9.45, T["title"], fontsize=19, color=INK, fontweight="bold", va="center")
    ax.text(0, 8.8, T["sub"], fontsize=13 * k, color=MUTED, va="center")
    cxs = [3.1, 9.2, 15.3, 21.4]
    for i, cx in enumerate(cxs):
        ax.add_patch(Circle((cx - 2.65, 7.9), 0.38, fc=STEPCOL[i], ec="none"))
        ax.text(cx - 2.65, 7.9, str(i + 1), ha="center", va="center", fontsize=15, color="white", fontweight="bold")
        ax.text(cx - 2.1, 7.9, T["t"][i], ha="left", va="center", fontsize=15.5 * k, color=INK, fontweight="bold")
        ax.text(cx, 2.35, T["c"][i], ha="center", va="center", fontsize=12 * k, color=MUTED, linespacing=1.3)
        if i < 3:
            x0a = (4.85, 11.65, 18.25)[i]
            ax.add_patch(FancyArrow(x0a, 5.0, 0.75, 0, width=0.34, head_width=0.8, head_length=0.4, fc=BL, ec="none", length_includes_head=True))
    # 1 webcam
    cx = cxs[0]
    ax.add_patch(Rectangle((cx - 0.55, 3.75), 1.1, 0.7, fc="#4B5563", ec="none"))
    ax.add_patch(FancyBboxPatch((cx - 1.0, 3.45), 2.0, 0.35, boxstyle="round,pad=0,rounding_size=0.15", fc="#374151", ec="none"))
    ax.add_patch(FancyBboxPatch((cx - 1.5, 4.4), 3.0, 2.5, boxstyle="round,pad=0,rounding_size=0.5", fc="#6B7280", ec="#374151", lw=1.5))
    ax.add_patch(Circle((cx, 5.65), 0.9, fc="#111827", ec="none")); ax.add_patch(Circle((cx, 5.65), 0.5, fc="#1F4E79", ec="none"))
    ax.add_patch(Circle((cx - 0.15, 5.8), 0.13, fc="white", ec="none", alpha=0.7)); ax.add_patch(Circle((cx + 1.1, 6.5), 0.1, fc="#34D399", ec="none"))
    # 2 hands -> numbers -> frames
    cx = cxs[1]; l = cx - 2.75
    ax.add_patch(FancyBboxPatch((l, 4.0), 1.9, 2.5, boxstyle="round,pad=0,rounding_size=0.12", fc="white", ec=BL, lw=1.6))
    skel(ax, A[FR], l + 0.1, 4.1, 1.7, 2.3)
    ax.add_patch(FancyArrow(l + 2.0, 5.25, 0.4, 0, width=0.16, head_width=0.45, head_length=0.25, fc=MUTED, ec="none"))
    for j in (3, 2, 1, 0):
        ax.add_patch(FancyBboxPatch((l + 2.55 + j * 0.28, 4.1 + j * 0.28), 1.55, 1.9, boxstyle="round,pad=0,rounding_size=0.1", fc="white" if j else BLF, ec=BL, lw=1.3, zorder=3 - j * 0.1 + 3))
    skel(ax, A[FR], l + 2.65, 4.2, 1.35, 1.7, lw=1.0)
    ax.text(l + 3.45, 3.55, T["frames"], ha="center", va="center", fontsize=12 * k, color=BL, fontweight="bold")
    ax.text(l + 0.95, 3.55, T["vals"], ha="center", va="center", fontsize=12 * k, color=BL, fontweight="bold")
    # 3 LSTM
    cx = cxs[2]
    ax.add_patch(FancyBboxPatch((cx - 2.7, 3.9), 5.4, 2.7, boxstyle="round,pad=0,rounding_size=0.25", fc=PURF, ec=PUR, lw=1.8))
    for j, lab in enumerate(("1", "2", "…", "30")):
        x = cx - 2.35 + j * 1.25
        ax.add_patch(FancyBboxPatch((x, 4.55), 0.95, 1.1, boxstyle="round,pad=0,rounding_size=0.12", fc="white", ec=PUR, lw=1.5))
        ax.text(x + 0.475, 5.1, lab, ha="center", va="center", fontsize=13, color=PUR, fontweight="bold")
        if j < 3: ax.add_patch(FancyArrow(x + 0.98, 5.1, 0.2, 0, width=0.08, head_width=0.3, head_length=0.1, fc=PUR, ec="none"))
    ax.text(cx, 6.15, "LSTM", ha="center", va="center", fontsize=14, color=PUR, fontweight="bold")
        # 4 output
    cx = cxs[3]
    ax.add_patch(FancyBboxPatch((cx - 1.6, 5.7), 3.2, 1.05, boxstyle="round,pad=0,rounding_size=0.2", fc="#FFE066", ec="#C9A400", lw=1.4))
    ax.text(cx, 6.22, T["word"], ha="center", va="center", fontsize=18 * k, color=INK, fontweight="bold")
    ax.text(cx, 5.35, T["ok"], ha="center", va="center", fontsize=11.5 * k, color=GREEN)
    ax.text(cx, 4.75, T["orr"], ha="center", va="center", fontsize=12 * k, color=MUTED)
    ax.add_patch(FancyBboxPatch((cx - 1.6, 3.55), 3.2, 0.95, boxstyle="round,pad=0,rounding_size=0.2", fc="#E5E7EB", ec="#9CA3AF", lw=1.4))
    ax.text(cx, 4.02, T["unsure"], ha="center", va="center", fontsize=16 * k, color=MUTED, fontweight="bold")
    ax.text(cx, 3.2, T["no"], ha="center", va="center", fontsize=11.5 * k, color="#B5483A")
    fig.savefig(os.path.join(out, f"fig24_overview4_{lang}.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

for lg in ("th", "en"): make(lg)
print("saved fig24_overview4_th/en in", out)
