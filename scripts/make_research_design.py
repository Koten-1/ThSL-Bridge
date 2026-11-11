# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Research design flow chart (5 stage groups, top to bottom).
Text and numbers are the ones already in the report: 5 deaf signers, MediaPipe 126 values/frame,
30 frames per sign, leave-one-signer-out (5 rounds), plain LSTM vs LSTM+DANN with 3 seeds.
  python3 scripts/make_research_design.py research/figures_v3/fig12_research_design.png        (Thai)
  python3 scripts/make_research_design.py research/figures_v3/fig12_research_design_en.png en  (English)
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

for fam in ("TH Sarabun New", "Thonburi", "Sukhumvit Set"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

INK = "#1F2937"
EN = len(sys.argv) > 2 and sys.argv[2] == "en"
if EN:
    plt.rcParams["font.family"] = "Helvetica"
groups_th = [
    ("1  เก็บข้อมูล", "#2B5F8E", [
        "บันทึกวิดีโอท่ามือ\n(สมาร์ตโฟน ผู้แสดงหูหนวก 5 คน)",
        "ชมรมฯ ยืนยัน\nรายการคำ"]),
    ("2  เตรียมข้อมูล", "#2E7D5B", [
        "สกัดจุดมือ\n(MediaPipe 126 ค่า/เฟรม)",
        "ตัดท่าอัตโนมัติ\nย่อเหลือ 30 เฟรม",
        "ตรวจข้อมูล\n(EDA)"]),
    ("3  วิธีที่ทดลอง", "#B8651B", [
        "จัดการมือซ้าย–ขวา",
        "ตำแหน่งมือเทียบใบหน้า"]),
    ("4  แบ่งข้อมูลและฝึก", "#6B4E9B", [
        "กันผู้แสดงทีละคน\n(5 รอบ)",
        "LSTM ปกติ เทียบกับ LSTM + DANN\n(3 ค่าเริ่มต้น)"]),
    ("5  ประเมิน", "#B5483A", [
        "ความแม่นยำ\nรายผู้แสดง",
        "เกณฑ์ความเชื่อมั่น\n(ตอบกี่ % แม่นเท่าไร)"]),
]

groups_en = [
    ("1  Data collection", "#2B5F8E", [
        "Record sign videos\n(smartphone,\n5 deaf signers)",
        "Deaf club confirms\nthe word list"]),
    ("2  Data preparation", "#2E7D5B", [
        "Extract hand points\n(MediaPipe,\n126 values/frame)",
        "Auto-cut each sign\nand resample\nto 30 frames",
        "Check the data\n(EDA)"]),
    ("3  Methods tested", "#B8651B", [
        "Left–right hand handling",
        "Hand position relative to the face"]),
    ("4  Split and train", "#6B4E9B", [
        "Hold out one signer at a time\n(5 rounds)",
        "Plain LSTM vs LSTM + DANN\n(3 random seeds)"]),
    ("5  Evaluate", "#B5483A", [
        "Accuracy per signer",
        "Confidence threshold\n(answers at what %\nare how accurate)"]),
]
groups = groups_en if EN else groups_th
FT, FB = (14, 11.5) if EN else (17, 13.5)

W, H = 6.6, 8.45
fig = plt.figure(figsize=(W, H), dpi=240, facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

gx0, gx1 = 0.35, W - 0.35
gh, gap = 1.34, 0.30
top = H - 0.2
for i, (title, col, items) in enumerate(groups):
    y1 = top - i * (gh + gap)
    y0 = y1 - gh
    ax.add_patch(FancyBboxPatch((gx0, y0), gx1 - gx0, gh, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="white", ec=col, lw=1.4, ls=(0, (5, 3))))
    ax.text(gx0 + 0.16, y1 - 0.14, title, ha="left", va="top", fontsize=FT, color=col, fontweight="bold")
    n = len(items)
    pad, sp = 0.18, 0.16
    bw = (gx1 - gx0 - 2 * pad - sp * (n - 1)) / n
    bh = 0.74
    by = y0 + 0.14
    for k, t in enumerate(items):
        bx = gx0 + pad + k * (bw + sp)
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=col, ec="none"))
        ax.text(bx + bw / 2, by + bh / 2, t, ha="center", va="center", fontsize=FB, color="white",
                linespacing=1.3)
    if i < len(groups) - 1:
        xm = W / 2
        ax.add_patch(FancyArrowPatch((xm, y0 - 0.02), (xm, y0 - gap + 0.02), arrowstyle="-|>",
                                     mutation_scale=16, lw=1.6, color=INK))

fig.savefig(sys.argv[1], facecolor="white")
print("saved", sys.argv[1])
