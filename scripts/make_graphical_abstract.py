# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Graphical abstract for the layered report (v5): three answers in one picture.
  1) the starting gap   2) what helps / what does not (change in points vs each experiment's own baseline)   3) can the confidence be trusted
Every number is copied from research/submission/report_th.md (tables 1, 3, 4, 6 and sections 4.3, 4.4, 4.7); nothing is computed from new runs.
  python3 scripts/make_graphical_abstract.py research/figures_v3/fig10_graphical_abstract.png
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

BLUE, ORANGE, GREEN, RED, INK, MUTED, PALE = "#2B5F8E", "#E08A2E", "#2E7D5B", "#B5483A", "#1F2937", "#4B5563", "#EAF1F8"
fig = plt.figure(figsize=(6.5, 3.15), dpi=240, facecolor="white")


def panel(ax_x, ax_w, hx, hw, num, title, color):
    ax = fig.add_axes([ax_x, 0.24, ax_w, 0.52])
    fig.patches.append(plt.Rectangle((hx, 0.83), hw, 0.14, transform=fig.transFigure, fc=color, ec="none"))
    fig.text(hx + 0.012, 0.90, f"{num}  {title}", color="white", fontsize=9, va="center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=7, length=2)
    return ax


# 1 the starting gap
a1 = panel(0.085, 0.20, 0.02, 0.262, "1", "ช่องว่างตั้งต้น", BLUE)
a1.bar([0, 1], [84.8, 51.9], color=[ORANGE, BLUE], width=0.62)
a1.set_xticks([0, 1]); a1.set_xticklabels(["แบ่งสุ่ม\n(เคยเห็นผู้แสดง)", "กันผู้แสดง\n(ผู้ใช้ใหม่)"], fontsize=7)
a1.set_xlim(-0.6, 2.0); a1.set_ylim(0, 108); a1.set_ylabel("ความแม่นยำ (%)", fontsize=7)
a1.text(0, 86.5, "84.8", ha="center", fontsize=9, fontweight="bold"); a1.text(1, 53.6, "51.9", ha="center", fontsize=9, fontweight="bold")
a1.plot([0.31, 1.45], [84.8, 84.8], color=MUTED, lw=0.7, ls=":")
a1.annotate("", xy=(1.45, 53), xytext=(1.45, 84.8), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.2))
a1.text(1.55, 68.5, "−33\nจุด", color=RED, fontsize=8.5, va="center")

# 2 helps / does not help
a2 = panel(0.585, 0.12, 0.305, 0.395, "2", "อะไรช่วย อะไรไม่ช่วย (จุด)", GREEN)
items = [("มือซ้าย–ขวา (13 คำ)", 15.9), ("เฉลี่ย 3 แบบจำลอง (28 คำ)", 6.0), ("ใบหน้าสัมพัทธ์ (13 คำ)", 5.9), ("DANN (28 คำ)", -5.6)]
ys = list(range(len(items)))[::-1]
a2.barh(ys, [v for _, v in items], color=[GREEN if v > 0 else RED for _, v in items], height=0.58)
a2.set_yticks(ys); a2.set_yticklabels([n for n, _ in items], fontsize=7.2)
a2.axvline(0, color=INK, lw=0.8); a2.set_xlim(-9, 21); a2.set_xlabel("เปลี่ยนจากฐานของแต่ละการทดลอง (จุด)", fontsize=6.8)
for y, (_, v) in zip(ys, items):
    a2.text(v + 0.5 if v > 0 else 0.6, y, f"{v:+.1f}".replace("-", "−"), va="center", ha="left", fontsize=8, color=INK)

# 3 can the confidence be trusted
a3 = panel(0.805, 0.18, 0.72, 0.27, "3", "เชื่อความเชื่อมั่นได้ไหม", ORANGE)
vals = [("สัญญา\n(แบ่งสุ่ม)", 95.4, MUTED), ("ได้จริง\n(ผู้ใช้ใหม่)", 66.2, RED), ("ตั้งจาก\nคนอื่น", 76.7, BLUE)]
a3.bar(range(3), [v for _, v, _ in vals], color=[c for _, _, c in vals], width=0.62)
a3.set_xticks(range(3)); a3.set_xticklabels([n for n, _, _ in vals], fontsize=6.8)
a3.set_ylim(0, 112); a3.axhline(90, color=GREEN, ls="--", lw=1.0); a3.text(2.45, 93, "เป้า 90", color=GREEN, fontsize=6.8, ha="right")
for i, (_, v, _) in enumerate(vals):
    a3.text(i, v + 2, f"{v}", ha="center", fontsize=8.5, fontweight="bold")
a3.text(2, 40, "ตอบ\n47%\nของท่า", ha="center", color="white", fontsize=6.6, fontweight="bold")
a3.set_ylabel("แม่นยำคำตอบที่รับ (%)", fontsize=6.6)

fig.text(0.02, 0.02, "ที่มา: การทดลองของทีม กันผู้แสดงทีละคน เฉลี่ย 3 ค่าเริ่มต้น (รายงานหัวข้อ 4.2 ถึง 4.7) ผลต่างแต่ละแถบเทียบกับฐานของการทดลองนั้นเอง จึงไม่ควรนำมาบวกกัน", fontsize=5.6, color=MUTED)
fig.savefig(sys.argv[1], facecolor="white")
print("saved", sys.argv[1])
