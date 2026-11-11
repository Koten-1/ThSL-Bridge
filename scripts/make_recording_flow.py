# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Flow chart of how the ThSL keypoint dataset was recorded and prepared, per signer (for the 'dataset and method' slide).

Every number is from the dataset card / extract reports: 3,004 + 4,193 videos, one sign per video, median 2.4 s, 75-105 repeats per word for S01-S03,
5-46 for S04-S05, MediaPipe Hands 126 values per frame, capture rule 200 ms, 30 frames, 7,168 signs.
  python3 scripts/make_recording_flow.py OUT.png
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib import font_manager

for fam in ("Sukhumvit Set", "Krungthep", "TH Sarabun New"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break

BLUE, PALE, ORANGE, RED, INK, MUTED = "#2B5F8E", "#E3ECF6", "#E08A2E", "#C0392B", "#1F2937", "#4B5563"
W, H = 100, 120
fig = plt.figure(figsize=(7.5, 9.0), dpi=200)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.add_patch(FancyBboxPatch((1.2, 1.2), 97.6, 117.6, boxstyle="round,pad=0,rounding_size=4", fc="white", ec=BLUE, lw=2.2))


def pill(cx, cy, w, h, main, sub=None, fc=PALE, ec=BLUE, size=15, bold=True):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=3.2", fc=fc, ec=ec, lw=1.6))
    if sub:
        ax.text(cx, cy + h * 0.16, main, ha="center", va="center", fontsize=size, fontweight="bold" if bold else "normal", color=INK)
        ax.text(cx, cy - h * 0.24, sub, ha="center", va="center", fontsize=size - 4.2, color=MUTED, linespacing=1.25)
    else:
        ax.text(cx, cy, main, ha="center", va="center", fontsize=size, fontweight="bold" if bold else "normal", color=INK)


def down(x, y0, y1):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="simple,head_width=7,head_length=6,tail_width=3", color=ORANGE, lw=0, mutation_scale=1))


cx = 50
ax.text(50, 113.2, "การบันทึกและเตรียมข้อมูล ต่อผู้แสดง 1 คน", ha="center", va="center", fontsize=17, fontweight="bold", color=BLUE)

pill(cx, 102, 70, 12.4, "ผู้แสดงหูหนวก (5 คน)", "สมาร์ตโฟน ส่วนใหญ่ 30 fps\nS01–S03 แนวนอน 1280×720 · S04–S05 แนวตั้ง ใกล้กล้อง", size=15)
down(cx, 95.2, 92.2)

# per-word group
ax.add_patch(Rectangle((9, 60), 82, 31.5, fc="none", ec=ORANGE, lw=1.8, ls=(0, (5, 3))))
ax.text(11.5, 88.6, "ต่อ 1 คำ (30 คำ)", ha="left", va="center", fontsize=13.5, fontweight="bold", color=ORANGE)
pill(cx - 4, 81, 56, 9.6, "ทำท่าคำนั้น 1 ครั้ง", "บันทึกเป็นวิดีโอสั้น 1 ไฟล์ (มัธยฐาน 2.4 วินาที)", size=14)
down(cx - 4, 75.8, 72.4)
pill(cx - 4, 67, 56, 9.6, "ทำซ้ำจนครบจำนวนต่อคำ", "S01–S03 ราว 75–105 ครั้ง · S04–S05 คำละ 5–46", size=14)
LB = "#3B82C4"
ax.plot([cx + 24, cx + 28.5, cx + 28.5, cx + 24.3], [67, 67, 81, 81], color=LB, lw=1.8)
ax.add_patch(FancyArrowPatch((cx + 28.5, 81), (cx + 24.2, 81), arrowstyle="-|>", mutation_scale=11, color=LB, lw=1.8))
ax.text(cx + 30.5, 74, "ซ้ำ", ha="left", va="center", fontsize=12.5, fontweight="bold", color=LB)

down(cx, 59.4, 56.2)
pill(cx, 51, 70, 10, "วิดีโอ 7,197 ไฟล์ (1 ท่าต่อไฟล์)", "ชุดแรก 3,004 + ชุดที่สอง 4,193 · ใช้ตามที่บันทึก ไม่ตัดต่อ ไม่หมุน", size=14)
down(cx, 45.4, 42.2)
pill(cx, 37, 70, 10, "MediaPipe Hands ตรวจจุดข้อต่อมือ", "21 จุด × (x, y, z) × 2 มือ = 126 ค่าต่อเฟรม", size=14)
down(cx, 31.4, 28.4)
pill(cx, 22.4, 70, 12.4, "กฎตัดท่า (ชุดเดียวกับเว็บแอป)", "เริ่มเมื่อมือเคลื่อนที่ · จบเมื่อมือนิ่ง 200 ms\nสุ่มเหลือ 30 เฟรม ได้อาร์เรย์ (30 × 126)", size=14)
down(cx, 15.8, 12.8)
ax.add_patch(FancyBboxPatch((8, 3.4), 84, 9.2, boxstyle="round,pad=0,rounding_size=3.2", fc="#FDF0E1", ec=ORANGE, lw=1.8))
ax.text(50, 9.6, "7,168 ท่า จาก 30 คำ", ha="center", va="center", fontsize=17, fontweight="bold", color=RED)
ax.text(50, 5.6, "เก็บเฉพาะตัวเลขจุดข้อต่อ ไม่มีภาพ ชื่อไฟล์ใช้รหัส · รวมผู้แสดงที่ได้ยิน 4 คน (53 ท่า คำ \"คุณ\")", ha="center", va="center", fontsize=9.4, color=MUTED)

fig.savefig(sys.argv[1], dpi=200, facecolor="white")
print("saved", sys.argv[1])
