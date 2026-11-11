# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""EDA square for the poster's data-collection row (4 panels, all counts from research/DATASET_CARD.md
and scripts/vocab.json, deaf signers S01-S05 only = 7,115 signs, 30 words):
  a) folder structure   b) signs per signer   c) signs per signer by word group   d) signers per word
  python3 scripts/make_eda_square.py research/figures_v3/fig14_eda_square.png
Also writes fig14a..d next to it.
"""
import sys, re, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle, FancyArrowPatch

for fam in ("TH Sarabun New", "Thonburi", "Sukhumvit Set"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

INK, MUTED, BLUE, LBLUE = "#1F2937", "#4B5563", "#2B5F8E", "#CFE0F0"
GROUPS = [("อาการและการแพ้", "#2B5F8E"), ("ส่วนของร่างกาย", "#6FA3CF"),
          ("บริการและยา", "#E08A2E"), ("คำทั่วไป", "#8FB996")]
ROLE2G = {"symptom": 0, "allergy": 0, "body_part": 1, "hospital": 2, "general": 3}

# ---- data from the dataset card ----
signers = ["S01", "S02", "S03", "S04", "S05"]
vocab = {w["th"]: w["role"] for w in json.load(open("scripts/vocab.json", encoding="utf-8"))["words"]}
table = {}
for line in open("research/DATASET_CARD.md", encoding="utf-8"):
    m = re.match(r"\| (\S+) \| ((?:\d+ \| ){9})(\d+) \|", line)
    if m and m.group(1) in vocab:
        v = [int(x) for x in m.group(2).replace("|", " ").split()]
        table[m.group(1)] = v[4:9]                      # S01..S05 only
words = list(table)
per_signer = np.array([sum(table[w][i] for w in words) for i in range(5)])
assert per_signer.sum() == 7115 and len(words) == 30, (per_signer.sum(), len(words))
by_group = np.zeros((4, 5))
for w in words:
    for i in range(5):
        by_group[ROLE2G[vocab[w]], i] += table[w][i]
n_sign = [sum(1 for w in words if table[w][i] >= 20) for i in range(5)]
cover = np.array([sum(1 for i in range(5) if table[w][i] >= 20) for w in words])
cover_hist = [int((cover == k).sum()) for k in range(1, 6)]
top2 = (per_signer[0] + per_signer[2]) / per_signer.sum() * 100

def folder(ax, x, y, w=0.9, h=0.62, fc=LBLUE, ec=BLUE):
    ax.add_patch(Polygon([[x, y], [x, y + h], [x + w * 0.38, y + h], [x + w * 0.46, y + h + 0.1],
                          [x + w, y + h + 0.1], [x + w, y]], closed=True, fc=fc, ec=ec, lw=1.2))

def panel_a(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    ax.set_title("ก  โครงสร้างโฟลเดอร์ของชุดข้อมูล", fontsize=15, color=INK, loc="left", fontweight="bold")
    folder(ax, 0.1, 2.9); ax.text(0.55, 2.7, "keypoints", ha="center", va="top", fontsize=11, color=INK)
    ys = [5.2, 4.3, 3.4, 2.5, 1.6]
    for y, s in zip(ys, signers):
        folder(ax, 2.9, y, w=0.8, h=0.5)
        ax.text(3.3, y + 0.2, s, ha="center", va="center", fontsize=11, color=INK, fontweight="bold") if False else None
        ax.text(3.9, y + 0.3, s, ha="left", va="center", fontsize=12, color=INK)
        ax.add_patch(FancyArrowPatch((1.0, 3.2), (2.85, y + 0.28), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=MUTED,
                                     connectionstyle="arc3,rad=0"))
    ax.plot([3.3]*3, [1.15, 0.95, 0.75], "o", ms=2.5, color=MUTED)
    # expand S01
    wy = [5.2, 4.2, 3.2]
    labs = ["ปวดท้อง", "ปวดหัว", "… รวม 30 คำ"]
    for y, l in zip(wy, labs):
        folder(ax, 5.9, y, w=0.7, h=0.45, fc="#FFF1D6", ec="#E08A2E")
        ax.text(6.75, y + 0.27, l, ha="left", va="center", fontsize=12, color=INK)
        ax.add_patch(FancyArrowPatch((4.55, 5.5), (5.85, y + 0.25), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=MUTED))
    ax.add_patch(FancyBboxPatch((6.0, 1.5), 3.8, 1.05, boxstyle="round,pad=0,rounding_size=0.1", fc="white", ec=BLUE, lw=1.1))
    ax.text(7.9, 2.17, "S01_ปวดท้อง_t01r01.npy", ha="center", va="center", fontsize=10.5, color=INK)
    ax.text(7.9, 1.83, "ตัวเลข 30 เฟรม × 126 ค่า", ha="center", va="center", fontsize=10.5, color=MUTED)
    ax.add_patch(FancyArrowPatch((6.3, 3.15), (6.5, 2.58), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=MUTED))
    ax.text(0.1, 0.15, "ชุดข้อมูลเก็บตัวเลขจุดมือ ไม่มีภาพหรือใบหน้า ใช้รหัสผู้แสดงแทนชื่อ", fontsize=10.5, color=MUTED)

def panel_b(ax):
    ax.set_title("ข  จำนวนท่าที่บันทึกได้ของผู้แสดงแต่ละคน", fontsize=15, color=INK, loc="left", fontweight="bold")
    b = ax.bar(signers, per_signer, color=BLUE, width=0.62)
    for r, v in zip(b, per_signer):
        ax.text(r.get_x() + r.get_width() / 2, v + 40, f"{v:,}", ha="center", fontsize=12, color=INK)
    ax.set_ylim(0, 3100); ax.set_ylabel("จำนวนท่า", fontsize=12); ax.set_xlabel("ผู้แสดงหูหนวก", fontsize=12)
    ax.tick_params(labelsize=12)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.text(0.98, 0.93, f"S01 และ S03 รวมกัน {top2:.0f}%\nของทั้งหมด {per_signer.sum():,} ท่า",
            transform=ax.transAxes, ha="right", va="top", fontsize=12, color="#B5483A")

def panel_c(ax):
    ax.set_title("ค  จำนวนท่าของผู้แสดงแต่ละคน แยกตามกลุ่มคำ", fontsize=15, color=INK, loc="left", fontweight="bold")
    bottom = np.zeros(5)
    for g, (name, col) in enumerate(GROUPS):
        ax.bar(signers, by_group[g], bottom=bottom, color=col, width=0.62, label=name)
        bottom += by_group[g]
    ax.set_ylim(0, 3100); ax.set_ylabel("จำนวนท่า", fontsize=12); ax.set_xlabel("ผู้แสดงหูหนวก", fontsize=12)
    ax.tick_params(labelsize=12)
    ax.legend(fontsize=11, frameon=False, loc="upper right")
    for s in ("top", "right"): ax.spines[s].set_visible(False)

def panel_d(ax):
    ax.set_title("ง  แต่ละคำมีผู้แสดงกี่คน (คนละอย่างน้อย 20 ท่า)", fontsize=15, color=INK, loc="left", fontweight="bold")
    xs = ["1", "2", "3", "4", "5"]
    cols = ["#B5483A" if k <= 2 else BLUE for k in range(1, 6)]
    b = ax.bar(xs, cover_hist, color=cols, width=0.62)
    for r, v in zip(b, cover_hist):
        ax.text(r.get_x() + r.get_width() / 2, v + 0.4, str(v), ha="center", fontsize=13, color=INK)
    ax.set_ylim(0, max(cover_hist) * 1.3)
    ax.set_xlabel("จำนวนผู้แสดงที่มีข้อมูลของคำนั้น (คน)", fontsize=12)
    ax.set_ylabel("จำนวนคำ", fontsize=12)
    ax.tick_params(labelsize=12)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    few = [w for w, c in zip(words, cover) if c <= 2]
    for k in (1, 2):
        names = " ".join(w for w, c in zip(words, cover) if c == k)
        ax.text(k - 1, cover_hist[k - 1] + 2.2, names, ha="center", fontsize=12, color="#B5483A")
    ax.text(0.98, 0.93, "คำที่มีผู้แสดงไม่เกิน 2 คน\nทดสอบกับผู้แสดงใหม่ได้ยาก" , transform=ax.transAxes,
            ha="right", va="top", fontsize=12, color="#B5483A")
    return few

if __name__ == "__main__":
    out = sys.argv[1]
    base, ext = os.path.splitext(out)
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 10.5), dpi=220, facecolor="white")
    panel_a(axs[0, 0]); panel_b(axs[0, 1]); panel_c(axs[1, 0]); few = panel_d(axs[1, 1])
    fig.tight_layout(h_pad=2.2, w_pad=2.2)
    fig.savefig(out, facecolor="white")
    for key, fn in (("a", panel_a), ("b", panel_b), ("c", panel_c), ("d", panel_d)):
        f, a = plt.subplots(figsize=(5.2, 5.2), dpi=220, facecolor="white")
        fn(a); f.tight_layout(); f.savefig(f"{base.replace('fig14_eda_square','fig14')}{key}{ext}", facecolor="white"); plt.close(f)
    print("signs per signer", dict(zip(signers, per_signer.tolist())), f"S01+S03 = {top2:.1f}%")
    print("words by number of signers with >=20 signs:", dict(zip(range(1, 6), cover_hist)))
    print("words with <=2 signers:", few)
    print("group totals:", {n: int(by_group[g].sum()) for g, (n, _) in enumerate(GROUPS)})
