# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""DANN idea figure (explanatory, NOT our result): circles = signers, squares/triangles = two words.
Original drawing (not copied from any source).
  python3 scripts/make_dann_idea.py research/figures_v3/fig21_dann_idea.png
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Ellipse

for fam in ("TH Sarabun New", "Thonburi"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam; break
INK, MUTED, PUR, TEAL, RED = "#1F2937", "#4B5563", "#6B4E9B", "#2E9CA6", "#B5483A"
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=220, facecolor="white")
ax.set_xlim(0, 14.6); ax.set_ylim(-0.9, 4.9); ax.set_aspect("equal"); ax.axis("off")

def pts(P, kind, col, s=95):
    P = np.array(P)
    ax.scatter(P[:, 0], P[:, 1], marker="s" if kind == "sq" else "^", s=s, facecolor="white", edgecolor=col, linewidth=1.8, zorder=4)

# ---- left: before ----
ax.add_patch(Circle((2.2, 2.0), 1.75, fc=PUR, alpha=0.12, ec=PUR, lw=1.6))
ax.add_patch(Circle((6.0, 2.0), 1.75, fc=TEAL, alpha=0.12, ec=TEAL, lw=1.6))
pts([(1.5, 2.9), (2.4, 3.2), (2.9, 2.6), (1.9, 2.5), (1.2, 2.7)], "sq", PUR); pts([(1.4, 1.2), (2.3, 0.9), (3.1, 1.3), (2.0, 1.5), (1.0, 1.5)], "tr", PUR)
pts([(5.5, 2.3), (6.4, 2.55), (6.9, 2.25), (5.4, 1.65), (6.2, 1.55), (6.8, 1.7)], "sq", TEAL); pts([(5.6, 0.95), (6.5, 0.8), (7.1, 1.15), (6.0, 1.2)], "tr", TEAL)
ax.plot([0.0, 8.3], [2.0, 2.0], color="#4B82E8", lw=1.8, ls=(0, (5, 3)), zorder=3)
ax.add_patch(Ellipse((6.2, 1.65), 2.3, 0.55, fc="none", ec=RED, lw=1.8, zorder=5))
ax.text(8.15, 2.12, "เส้นแบ่งคำ", color="#4B82E8", fontsize=12, ha="right")
ax.text(2.2, 4.0, "ผู้แสดง A", ha="center", fontsize=14, color=PUR, fontweight="bold")
ax.text(6.0, 4.0, "ผู้แสดง B", ha="center", fontsize=14, color=TEAL, fontweight="bold")
ax.text(4.1, -0.35, "ก่อน: ข้อมูลของแต่ละคนแยกเป็นกลุ่ม\nเส้นแบ่งที่เรียนจากคนหนึ่ง ใช้กับอีกคนผิด (วงแดง)", ha="center", va="center", fontsize=12.5, color=INK, linespacing=1.3)
# ---- right: goal ----
ax.add_patch(Circle((10.9, 2.0), 1.75, fc=PUR, alpha=0.12, ec=PUR, lw=1.6))
ax.add_patch(Circle((12.4, 2.0), 1.75, fc=TEAL, alpha=0.12, ec=TEAL, lw=1.6))
pts([(10.4, 2.9), (11.2, 3.1), (11.6, 2.6), (10.8, 2.5)], "sq", PUR); pts([(10.5, 1.2), (11.3, 0.9), (11.9, 1.4)], "tr", PUR)
pts([(12.2, 2.8), (12.9, 2.5), (11.9, 3.0), (12.6, 2.9)], "sq", TEAL); pts([(12.0, 1.1), (12.8, 1.3), (12.5, 0.8)], "tr", TEAL)
ax.plot([9.3, 14.4], [2.0, 2.0], color="#2E7D5B", lw=1.8, ls=(0, (5, 3)), zorder=3)
ax.text(14.35, 2.12, "เส้นแบ่งเดียว", color="#2E7D5B", fontsize=12, ha="right")
ax.text(11.65, 4.0, "เป้าหมายของ DANN", ha="center", fontsize=14, color=INK, fontweight="bold")
ax.text(11.65, -0.35, "กลุ่มซ้อนกัน แยกไม่ออกว่าใครทำ\nเส้นแบ่งเดียวใช้ได้กับทุกคน", ha="center", va="center", fontsize=12.5, color=INK, linespacing=1.3)
# legend
ax.scatter([0.35], [4.55], marker="s", s=70, facecolor="white", edgecolor=INK, lw=1.6); ax.text(0.6, 4.55, "คำที่ 1", va="center", fontsize=12)
ax.scatter([1.9], [4.55], marker="^", s=70, facecolor="white", edgecolor=INK, lw=1.6); ax.text(2.15, 4.55, "คำที่ 2", va="center", fontsize=12)
ax.text(14.4, 4.6, "ภาพอธิบายแนวคิด ไม่ใช่ผลของเรา", ha="right", fontsize=12, color=RED, fontweight="bold")
ax.annotate("", xy=(9.0, 2.0), xytext=(8.6, 2.0), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.5))
fig.savefig(sys.argv[1], facecolor="white", bbox_inches="tight", pad_inches=0.1); print("saved", sys.argv[1])
