# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Stage 3 (วิธีที่ทดลอง) cards, concept only (results live in the RESULT panel).
Definitions from research/submission/report_th.md sections 3.4(e), 4.5 and 4.6.
  python3 scripts/make_stage3_cards.py research/figures_v3
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch

for fam in ("TH Sarabun New", "Thonburi"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam; break
plt.rcParams["axes.unicode_minus"] = False
INK, MUTED, BLUE, LBLUE, ORANGE, GRAY = "#1F2937", "#4B5563", "#4B82E8", "#DCE7FB", "#E08A2E", "#E6E8EC"
out = sys.argv[1]

def slots(ax, x, y, active, w=0.62, h=0.5):
    """two slot boxes; active = 0 or 1 (the main hand)"""
    for k in (0, 1):
        ax.add_patch(FancyBboxPatch((x + k * (w + 0.08), y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=BLUE if k == active else GRAY, ec="none"))
        if k == active:
            ax.add_patch(Circle((x + k * (w + 0.08) + w / 2, y + h / 2), 0.12, fc="white", ec="none"))

def fig18():
    fig, ax = plt.subplots(figsize=(7.4, 4.9), dpi=220, facecolor="white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")
    ax.text(0, 6.35, "มือซ้าย–ขวา: ทดลอง 3 แบบ", fontsize=17, color=INK, fontweight="bold", va="center")
    ax.text(0, 5.72, "MediaPipe แยกมือเป็น 2 ช่อง แต่มือที่ใช้ขยับมากอยู่คนละช่องในแต่ละคน", fontsize=12.5, color=MUTED, va="center")
    # who has the main hand where
    for i, (s, pct, a) in enumerate((("S01", "79%", 0), ("S03", "88%", 0), ("S02", "76%", 1))):
        x = 0.1 + i * 3.2
        ax.text(x, 5.05, s, fontsize=14, color=INK, fontweight="bold", va="center")
        slots(ax, x + 0.65, 4.8, a, w=0.5, h=0.46)
        ax.text(x + 2.0, 5.05, f"{pct}", fontsize=13, color=BLUE, va="center", fontweight="bold")
    ax.text(0.1, 4.45, "ซ้าย = ช่อง 1, ขวา = ช่อง 2, วงกลม = มือที่ขยับมาก, ตัวเลข = สัดส่วนครั้งที่มือหลักอยู่ช่องนั้น", fontsize=10.5, color=MUTED, va="center")
    rows = [
        ("1", "ไม่จัดการ", "ใช้ช่องตามที่ MediaPipe ให้", ("same",)),
        ("2", "พลิกตอนฝึก", "สลับช่องและพลิกซ้ายขวาของข้อมูลฝึกแบบสุ่ม (โอกาส 0.5)", ("swap",)),
        ("3", "ปรับทุกคลิป", "ย้ายมือหลักไปอยู่ช่อง 1 เสมอ", ("fix",)),
    ]
    for i, (n, name, desc, kind) in enumerate(rows):
        y = 3.4 - i * 1.25
        ax.add_patch(FancyBboxPatch((0, y - 0.45), 10, 1.0, boxstyle="round,pad=0,rounding_size=0.1", fc="#F6F8FC", ec=LBLUE, lw=1))
        ax.add_patch(Circle((0.45, y + 0.05), 0.28, fc=BLUE, ec="none"))
        ax.text(0.45, y + 0.04, n, ha="center", va="center", fontsize=15, color="white", fontweight="bold")
        ax.text(0.95, y + 0.28, name, fontsize=14.5, color=INK, fontweight="bold", va="center")
        ax.text(0.95, y - 0.17, desc, fontsize=11.5, color=MUTED, va="center")
        # mini diagram on the right
        x0 = 6.3
        if kind[0] == "same":
            slots(ax, x0, y - 0.2, 0, w=0.5, h=0.42); slots(ax, x0 + 1.4, y - 0.2, 1, w=0.5, h=0.42)
        elif kind[0] == "swap":
            slots(ax, x0, y - 0.2, 0, w=0.5, h=0.42)
            ax.add_patch(FancyArrowPatch((x0 + 1.25, y + 0.01), (x0 + 1.75, y + 0.01), arrowstyle="<|-|>", mutation_scale=12, color=MUTED, lw=1.4))
            slots(ax, x0 + 1.9, y - 0.2, 1, w=0.5, h=0.42)
        else:
            slots(ax, x0, y - 0.2, 1, w=0.5, h=0.42)
            ax.add_patch(FancyArrowPatch((x0 + 1.25, y + 0.01), (x0 + 1.7, y + 0.01), arrowstyle="-|>", mutation_scale=12, color=MUTED, lw=1.4))
            slots(ax, x0 + 1.85, y - 0.2, 0, w=0.5, h=0.42)
    fig.savefig(os.path.join(out, "fig18_leftright_card.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

def person(ax, cx, base, head_r, neck_off, hand_off, torso_w):
    neck = base + neck_off
    ax.add_patch(FancyBboxPatch((cx - torso_w / 2, base), torso_w, neck_off, boxstyle="round,pad=0,rounding_size=0.2", fc=LBLUE, ec="none"))
    hc = neck + head_r + 0.05
    ax.add_patch(Circle((cx, hc), head_r, fc=LBLUE, ec=BLUE, lw=1.4))
    hand = (cx + head_r * 0.25, neck - hand_off)
    ax.add_patch(Circle(hand, 0.11, fc=ORANGE, ec="none", zorder=4))
    ax.add_patch(FancyArrowPatch((cx - head_r, hc), (cx + head_r, hc), arrowstyle="<|-|>", mutation_scale=9, color=INK, lw=1.2, zorder=5))
    ax.plot([cx, hand[0]], [hc, hand[1]], color=ORANGE, lw=1.3, ls=(0, (3, 2)), zorder=3)

def fig19():
    fig, ax = plt.subplots(figsize=(7.4, 4.9), dpi=220, facecolor="white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")
    ax.text(0, 6.35, "ตำแหน่งมือเทียบใบหน้า", fontsize=17, color=INK, fontweight="bold", va="center")
    ax.text(0, 5.72, "พิกัดดิบเป็นสัดส่วนของภาพ จึงเปลี่ยนตามระยะและท่านั่ง", fontsize=12.5, color=MUTED, va="center")
    for x0, close in ((0.2, True), (5.2, False)):
        ax.add_patch(Rectangle((x0, 1.25), 4.6, 3.9, fc="white", ec="#9AA3B2", lw=1.4))
        if close:
            person(ax, x0 + 2.3, 1.25, 0.72, 1.65, 1.2, 3.0)
            ax.text(x0 + 2.3, 0.85, "นั่งใกล้กล้อง: มืออยู่ชิดขอบล่างของภาพ", ha="center", fontsize=11.5, color=MUTED)
        else:
            person(ax, x0 + 2.3, 1.25, 0.42, 2.1, 0.7, 1.7)
            ax.text(x0 + 2.3, 0.85, "นั่งไกลกว่า: ท่าเดียวกัน แต่มืออยู่สูงขึ้นในภาพ", ha="center", fontsize=11.5, color=MUTED)
    ax.text(5.0, 0.28, "วิธีที่ทดลอง: วัดมือเป็นกี่เท่าของความกว้างใบหน้า (ลูกศรสองหัว) เพื่อไม่ขึ้นกับระยะที่นั่งจากกล้อง",
            ha="center", fontsize=11.5, color=BLUE, fontweight="bold")
    fig.savefig(os.path.join(out, "fig19_face_relative_card.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

fig18(); fig19(); print("saved fig18, fig19 in", out)
