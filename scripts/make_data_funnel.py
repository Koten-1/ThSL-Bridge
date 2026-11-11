# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Data funnel: videos recorded -> signs kept -> signs the 28-word classifier uses.
All numbers are counted from files on disk, nothing is estimated:
  videos  7,267 = extract_report.csv rows: setA 3,004 + setB 4,193 + hearing 70
  signs   7,168 = research/DATASET_CARD.md total (setA 2,993 + setB 4,122 + hearing 53)
  lost      99 = 11 (set 1, too few signs) + 71 (set 2, net of 80 too few and 9 too many) + 17 (hearing, no sign captured)
  28 words 6,688 = 7,168 - 195 (หมอ) - 285 (ขา); of the 285 ขา signs, 78 were flagged cut_by_edge (research/eda_all/report.md)
  python3 scripts/make_data_funnel.py research/figures_v3/fig11_data_funnel.png
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for fam in ("Sukhumvit Set", "Krungthep", "TH Sarabun New"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GREEN, RED, INK, MUTED = "#2B5F8E", "#E08A2E", "#2E7D5B", "#B5483A", "#1F2937", "#4B5563"
rows = [  # (label, value, colour)
    ("วิดีโอที่บันทึก", 7267, MUTED),
    ("ท่าที่ตัดได้ (30 คำ)", 7168, BLUE),
    ("ท่าที่ใช้ฝึก (28 คำ)", 6688, GREEN),
]
notes = [
    "",
    "ต่างกัน 99 วิดีโอ: ชุดแรก 11 · ชุดสอง 71 (สุทธิ) · ผู้ได้ยิน 17\n(ตัดได้ท่าน้อยกว่าที่ควร หรือไม่พบท่า)",
    "ตัดคำ หมอ (195 ท่า) และ ขา (285 ท่า) ออกจากตัวจำแนก\nขา: 78 ท่ามือหลุดกรอบภาพ",
]

fig, ax = plt.subplots(figsize=(6.5, 2.5), dpi=240, facecolor="white")
ys = [2, 1, 0]
ax.barh(ys, [v for _, v, _ in rows], color=[c for _, _, c in rows], height=0.62)
for y, (lab, v, _) in zip(ys, rows):
    ax.text(-150, y, lab, ha="right", va="center", fontsize=8.5, color=INK)
    ax.text(v - 120, y, f"{v:,}", ha="right", va="center", fontsize=11, color="white", fontweight="bold")
for y, n in zip(ys, notes):
    if n:
        ax.text(7567, y, n, ha="left", va="center", fontsize=6.6, color=MUTED, linespacing=1.35)
# step arrows
for y0, y1, d in ((2, 1, "−99"), (1, 0, "−480")):
    ax.text(6900 if y0 == 2 else 6450, (y0 + y1) / 2, d, ha="center", va="center", fontsize=8, color=RED, fontweight="bold")
ax.set_xlim(0, 7267)
ax.set_ylim(-0.5, 2.5)
ax.axis("off")
fig.subplots_adjust(left=0.20, right=0.60, top=0.97, bottom=0.12)
fig.text(0.02, 0.02, "ที่มา: รายงานการสกัดและตรวจข้อมูลของทีม (หนึ่งวิดีโอให้ท่าได้ 0 ถึงหลายท่า ตัวเลข −99 เป็นผลต่างสุทธิ) ไม่พบท่าที่ค่าไม่ครบ ไม่มีมือ หรือนิ่งในชุดของผู้แสดงหูหนวก",
         fontsize=5.4, color=MUTED)
fig.savefig(sys.argv[1], facecolor="white")
print("saved", sys.argv[1])
