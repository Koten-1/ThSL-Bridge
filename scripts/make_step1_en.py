# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Step 1 (orange) cards in English: folder structure, signs per signer, data funnel, what the data looks like.
Numbers: research/DATASET_CARD.md, make_data_funnel.py, make_data_look.py (real keypoints, no photos).
  python3 scripts/make_step1_en.py KEYPOINT_ROOT OUT_DIR
"""
import sys, os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle, FancyArrowPatch
plt.rcParams["font.family"] = "Helvetica"
root, out = os.path.expanduser(sys.argv[1]), sys.argv[2]
OR, ORF, ORD, INK, MUTED, RED = "#F0953A", "#FDEBD6", "#C9701A", "#1F2937", "#4B5563", "#B5483A"
EDGES = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
signers = ["S01", "S02", "S03", "S04", "S05"]; counts = [2666, 1061, 2543, 703, 142]
top2 = (counts[0] + counts[2]) / sum(counts) * 100

def folder(ax, x, y, w=0.9, h=0.62, fc=ORF, ec=OR):
    ax.add_patch(Polygon([[x, y], [x, y + h], [x + w * 0.38, y + h], [x + w * 0.46, y + h + 0.1], [x + w, y + h + 0.1], [x + w, y]], closed=True, fc=fc, ec=ec, lw=1.3))

def card_a():
    fig, ax = plt.subplots(figsize=(5.6, 4.6), dpi=220, facecolor="white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")
    ax.text(0, 6.35, "How the dataset is organised", fontsize=14, color=INK, fontweight="bold", va="center")
    folder(ax, 0.1, 2.8); ax.text(0.55, 2.6, "keypoints", ha="center", va="top", fontsize=10, color=INK)
    for y, s in zip([5.0, 4.15, 3.3, 2.45, 1.6], signers):
        folder(ax, 2.9, y, w=0.8, h=0.5); ax.text(3.9, y + 0.3, s, ha="left", va="center", fontsize=11, color=INK)
        ax.add_patch(FancyArrowPatch((1.0, 3.1), (2.85, y + 0.28), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=MUTED))
    ax.plot([3.3] * 3, [1.2, 1.0, 0.8], "o", ms=2.5, color=MUTED)
    for y, l in zip([5.0, 4.05, 3.1], ["pain in stomach", "headache", "... 30 words"]):
        folder(ax, 5.7, y, w=0.7, h=0.45, fc="#FFF6E5", ec=ORD); ax.text(6.55, y + 0.27, l, ha="left", va="center", fontsize=10.5, color=INK)
        ax.add_patch(FancyArrowPatch((4.45, 5.3), (5.65, y + 0.25), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=MUTED))
    ax.add_patch(FancyBboxPatch((5.6, 1.35), 4.2, 1.05, boxstyle="round,pad=0,rounding_size=0.1", fc="white", ec=OR, lw=1.3))
    ax.text(7.7, 2.02, "S01_<word>_t01r01.npy", ha="center", va="center", fontsize=9.5, color=INK)
    ax.text(7.7, 1.65, "30 frames × 126 numbers", ha="center", va="center", fontsize=9.5, color=MUTED)
    ax.add_patch(FancyArrowPatch((6.0, 3.05), (6.3, 2.45), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=MUTED))
    ax.text(0.1, 0.15, "Numbers only: no images or faces. Signer codes, not names.", fontsize=9.5, color=MUTED)
    fig.savefig(os.path.join(out, "fig14a_en.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

def card_b():
    fig, ax = plt.subplots(figsize=(5.6, 4.6), dpi=220, facecolor="white")
    b = ax.bar(signers, counts, color=OR, width=0.62)
    for r, v in zip(b, counts): ax.text(r.get_x() + r.get_width() / 2, v + 40, f"{v:,}", ha="center", fontsize=11.5, color=INK)
    ax.set_ylim(0, 3100); ax.set_ylabel("Signs recorded", fontsize=11); ax.set_xlabel("Deaf signer", fontsize=11); ax.tick_params(labelsize=11)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_title("Signs recorded per signer", fontsize=14, color=INK, loc="left", fontweight="bold")
    ax.text(0.98, 0.93, f"S01 and S03 together:\n{top2:.0f}% of {sum(counts):,} signs", transform=ax.transAxes, ha="right", va="top", fontsize=11.5, color=RED)
    fig.savefig(os.path.join(out, "fig14b_en.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

def funnel():
    rows = [("Videos recorded", 7267, "#9CA3AF"), ("Signs cut (30 words)", 7168, ORD), ("Signs used (28 words)", 6688, OR)]
    notes = ["", "99 fewer: a video can give\nno sign or several signs", "Words ‘doctor’ (195) and ‘leg’ (285) left out\n‘leg’: 78 signs had the hand cut off by the frame edge"]
    fig, ax = plt.subplots(figsize=(7.4, 3.2), dpi=220, facecolor="white")
    ys = [2, 1, 0]
    ax.barh(ys, [v for _, v, _ in rows], color=[c for _, _, c in rows], height=0.62)
    for y, (lab, v, _) in zip(ys, rows):
        ax.text(-150, y, lab, ha="right", va="center", fontsize=10.5, color=INK); ax.text(v - 120, y, f"{v:,}", ha="right", va="center", fontsize=12.5, color="white", fontweight="bold")
    for y, n in zip(ys, notes):
        if n: ax.text(7567, y, n, ha="left", va="center", fontsize=8.2, color=MUTED, linespacing=1.35)
    for y0, y1, d, x in ((2, 1, "−99", 6900), (1, 0, "−480", 6450)): ax.text(x, (y0 + y1) / 2, d, ha="center", va="center", fontsize=10, color=RED, fontweight="bold")
    ax.set_xlim(0, 7267); ax.set_ylim(-0.5, 2.5); ax.axis("off")
    fig.subplots_adjust(left=0.22, right=0.62, top=0.95, bottom=0.12)
    fig.savefig(os.path.join(out, "fig11_data_funnel_en.png"), facecolor="white"); plt.close(fig)

def look():
    word = "ขอบคุณ"
    arrs = {s: np.load(sorted(glob.glob(f"{root}/{s}/{word}/*.npy"))[0]).astype(float) for s in ("S01", "S03")}
    def bbox(a):
        pts = np.concatenate([a[:, k * 63:(k + 1) * 63].reshape(-1, 21, 3)[:, :, :2].reshape(-1, 2) for k in (0, 1)]); pts = pts[np.abs(pts).sum(1) > 0]; return pts.min(0), pts.max(0)
    bb = {s: bbox(a) for s, a in arrs.items()}; HALF = max((hi - lo).max() for lo, hi in bb.values()) / 2 + 0.03
    frames = [0, 6, 12, 18, 24, 29]
    fig = plt.figure(figsize=(13, 5.6), dpi=200, facecolor="white")
    gs = fig.add_gridspec(2, 6, left=0.07, right=0.55, top=0.82, bottom=0.16, wspace=0.08, hspace=0.12)
    for r, s in enumerate(("S01", "S03")):
        a = arrs[s]
        for c, f in enumerate(frames):
            ax = fig.add_subplot(gs[r, c]); ctr = (bb[s][0] + bb[s][1]) / 2
            ax.set_xlim(ctr[0] - HALF, ctr[0] + HALF); ax.set_ylim(ctr[1] + HALF, ctr[1] - HALF); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values(): sp.set_color("#C7CDD6")
            for slot, col in ((0, "#2B5F8E"), (1, OR)):
                h = a[f, slot * 63:(slot + 1) * 63].reshape(21, 3)
                if not h.any(): continue
                for i, j in EDGES: ax.plot([h[i, 0], h[j, 0]], [h[i, 1], h[j, 1]], color=col, lw=1.6)
                ax.scatter(h[:, 0], h[:, 1], s=9, color=col, zorder=3)
            if r == 0: ax.set_title(f"frame {f + 1}", fontsize=11, color=MUTED)
            if c == 0: ax.set_ylabel(s, fontsize=14, color=INK, rotation=0, labelpad=22, va="center", fontweight="bold")
    fig.text(0.07, 0.93, "The same word (‘thank you’) signed by two people", fontsize=16, color=INK, fontweight="bold")
    fig.text(0.07, 0.03, "Drawn from the saved hand-point numbers, not from video. Blue and orange = the two hand slots.", fontsize=10.5, color=MUTED)
    ax = fig.add_axes([0.62, 0.2, 0.36, 0.62]); ax.imshow(arrs["S01"], aspect="auto", cmap="viridis", interpolation="nearest"); ax.axvline(62.5, color="white", lw=1.5)
    ax.set_xticks([31, 94]); ax.set_xticklabels(["hand slot 1\n(63 values)", "hand slot 2\n(63 values)"], fontsize=10.5)
    ax.set_yticks([0, 9, 19, 29]); ax.set_yticklabels(["1", "10", "20", "30"], fontsize=10.5); ax.set_ylabel("frame (30 frames)", fontsize=11.5)
    ax.set_title("What the model really receives (S01): 30 × 126", fontsize=14, color=INK, loc="left", fontweight="bold")
    fig.text(0.62, 0.03, "Flat bands = no hand found in that frame (stored as zero)", fontsize=10.5, color=MUTED)
    fig.savefig(os.path.join(out, "fig17_data_look_en.png"), facecolor="white"); plt.close(fig)

card_a(); card_b(); funnel(); look(); print("saved step 1 English figures in", out)
