# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Two method diagrams for the poster's METHODOLOGY panel.
  fig15  how one sign is cut (capture rule: scripts/capture_rule.py; numbers from research/DATASET_CARD.md section 4)
         the movement curve is an ILLUSTRATION, not a measured clip
  fig16  the 5 leave-one-signer-out rounds (tested-sign counts from research/loso_final28/summary.md)
  python3 scripts/make_method_figs.py research/figures_v3
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, FancyArrow

for fam in ("TH Sarabun New", "Thonburi", "Sukhumvit Set"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False
INK, MUTED, GREEN, PURPLE, ORANGE, RED = "#1F2937", "#4B5563", "#2E7D5B", "#6B4E9B", "#E08A2E", "#B5483A"
out = sys.argv[1]

# ---------- fig15: how one sign is cut (step 2, peach). Read at a glance: start -> kept -> end -> 30 frames ----------
def fig15(lang="th"):
    en = lang == "en"
    plt.rcParams["font.family"] = "Helvetica" if en else "TH Sarabun New"
    k = 0.8 if en else 1.0
    PE, PED, PEL = "#F0A34A", "#C9701A", "#FDEBD6"
    T = dict(title="How one sign is cut" if en else "ตัดท่า: หนึ่งท่าถูกตัดอย่างไร",
             badge="Illustration, not real data" if en else "ภาพตัวอย่าง ไม่ใช่ข้อมูลจริง",
             still="hand still" if en else "มือนิ่ง", kept="sign kept" if en else "ท่าที่เก็บ",
             start="START" if en else "เริ่ม", end="END" if en else "จบ",
             d1="the hand starts to move" if en else "มือเริ่มขยับ", d2="the hand is still for 0.2 s" if en else "มือนิ่ง 0.2 วินาที",
             r1="Resampled to 30 frames" if en else "ย่อเหลือ 30 เฟรม", r2="each frame = 126 values" if en else "แต่ละเฟรม = 126 ค่า")
    fig, ax = plt.subplots(figsize=(8.6, 5.2), dpi=220, facecolor="white")
    ax.set_xlim(0, 20); ax.set_ylim(0, 11); ax.axis("off")
    ax.text(0, 10.3, T["title"], fontsize=21 * k, color=INK, fontweight="bold", va="center")
    ax.add_patch(FancyBboxPatch((20 - (7.6 if en else 6.9), 9.6), 7.6 if en else 6.9, 1.35, boxstyle="round,pad=0,rounding_size=0.25", fc="#FFF4D6", ec="#C9A400", lw=2))
    ax.text(20 - (3.8 if en else 3.45), 10.28, T["badge"], ha="center", va="center", fontsize=15 * k, color="#7A5B00", fontweight="bold")
    x1, x2 = 4.3, 15.3
    ax.add_patch(Rectangle((0, 4.8), x1, 3.8, fc="#EEF0F3", ec="none")); ax.add_patch(Rectangle((x1, 4.8), x2 - x1, 3.8, fc=PEL, ec="none"))
    ax.add_patch(Rectangle((x2, 4.8), 19.9 - x2, 3.8, fc="#EEF0F3", ec="none"))
    t = np.linspace(0, 19.9, 800)
    sm = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
    env = sm((t - x1) / 0.9) * (1 - sm((t - (x2 - 0.9)) / 0.9))
    y = 5.15 + env * (1.7 + 0.55 * np.sin((t - x1) * 1.35))
    ax.plot(t, y, color=PED, lw=4, solid_capstyle="round", zorder=4)
    ax.text(x1 / 2, 8.05, T["still"], ha="center", va="center", fontsize=15 * k, color=MUTED)
    ax.text((x1 + x2) / 2, 8.05, T["kept"], ha="center", va="center", fontsize=19 * k, color=PED, fontweight="bold")
    ax.text((x2 + 19.9) / 2, 8.05, T["still"], ha="center", va="center", fontsize=15 * k, color=MUTED)
    for x, lab in ((x1, T["start"]), (x2, T["end"])):
        ax.plot([x, x], [4.8, 8.6], color=INK, lw=2.4, zorder=5)
        ax.add_patch(FancyBboxPatch((x - 1.15, 3.55), 2.3, 1.05, boxstyle="round,pad=0,rounding_size=0.2", fc=INK, ec="none", zorder=6))
        ax.text(x, 4.08, lab, ha="center", va="center", fontsize=17 * k, color="white", fontweight="bold", zorder=7)
    ax.text(x1, 3.05, T["d1"], ha="center", va="center", fontsize=15 * k, color=INK)
    ax.text(x2, 3.05, T["d2"], ha="center", va="center", fontsize=15 * k, color=INK)
    ax.add_patch(FancyArrow(9.8, 2.75, 0, -0.55, width=0.55, head_width=1.1, head_length=0.35, fc=PE, ec="none", length_includes_head=True))
    for xx in np.linspace(x1 + 0.3, x2 - 0.3, 30):
        ax.add_patch(Rectangle((xx - 0.13, 1.1), 0.26, 0.85, fc=PE, ec="none"))
    ax.text(9.8, 0.5, T["r1"], ha="center", va="center", fontsize=18 * k, color=INK, fontweight="bold")
    ax.text(15.6, 0.5, "(" + T["r2"] + ")", ha="left", va="center", fontsize=12.5 * k, color=MUTED)
    fig.savefig(os.path.join(out, "fig15_capture_timeline" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

# ---------- fig16: 5 leave-one-signer-out rounds ----------
def fig16():
    signers = ["S01", "S02", "S03", "S04", "S05"]
    tested = [2464, 993, 2409, 643, 126]
    fig, ax = plt.subplots(figsize=(8.6, 5.2), dpi=220, facecolor="white")
    ax.set_xlim(-1.6, 7.4); ax.set_ylim(-0.2, 6.2); ax.axis("off")
    ax.set_title("กันผู้แสดงทีละคน: 5 รอบ", fontsize=17, color=INK, loc="left", fontweight="bold")
    cw, ch, gx, gy = 1.0, 0.72, 0.08, 0.16
    for j, s in enumerate(signers):
        ax.text(j * (cw + gx) + cw / 2, 5.55, s, ha="center", fontsize=14, color=INK, fontweight="bold")
    ax.text(5 * (cw + gx) + 0.7, 5.55, "ท่าที่ใช้ทดสอบ", ha="left", fontsize=13, color=INK, fontweight="bold")
    for r in range(5):
        y = 4.55 - r * (ch + gy)
        ax.text(-0.15, y + ch / 2, f"รอบ {r + 1}", ha="right", va="center", fontsize=14, color=INK)
        for j in range(5):
            test = (j == r)
            ax.add_patch(FancyBboxPatch((j * (cw + gx), y), cw, ch, boxstyle="round,pad=0,rounding_size=0.08",
                                        fc=PURPLE if test else "#E4DDF0", ec="none"))
            ax.text(j * (cw + gx) + cw / 2, y + ch / 2, "ทดสอบ" if test else "ฝึก", ha="center", va="center",
                    fontsize=13, color="white" if test else "#8C7BB0", fontweight="bold" if test else "normal")
        ax.text(5 * (cw + gx) + 0.7, y + ch / 2, f"{tested[r]:,} ท่า", ha="left", va="center", fontsize=14, color=INK)
    # legend + notes
    ax.add_patch(FancyBboxPatch((0.0, -0.15), 0.34, 0.26, boxstyle="round,pad=0,rounding_size=0.04", fc="#E4DDF0", ec="none"))
    ax.text(0.45, -0.02, "ฝึกจากผู้แสดงที่เหลือ", fontsize=12.5, va="center", color=INK)
    ax.add_patch(FancyBboxPatch((2.65, -0.15), 0.34, 0.26, boxstyle="round,pad=0,rounding_size=0.04", fc=PURPLE, ec="none"))
    ax.text(3.1, -0.02, "ผู้แสดงที่ระบบไม่เคยเห็น", fontsize=12.5, va="center", color=INK)
    ax.text(5.8, -0.02, "แต่ละรอบซ้ำ 3 ค่าเริ่มต้น", fontsize=12.5, va="center", color=MUTED, ha="left")
    ax.text(-1.5, 5.95, "ตั้งค่าการฝึกไว้ก่อนทดสอบ (60 รอบ · อัตราเรียนรู้ 0.001 · ชุดละ 16) ไม่ปรับตามผู้ทดสอบ",
            fontsize=12, color=PURPLE, ha="left")
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig16_loso_rounds.png"), facecolor="white"); plt.close(fig)

fig15(); fig15('en'); print("saved fig15 in", out)
