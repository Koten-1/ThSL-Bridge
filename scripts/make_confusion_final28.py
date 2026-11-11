# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Confusion matrix of the final 28-word leave-one-signer-out run (plain LSTM, seed-averaged
out-of-fold predictions, 6,635 test signs). Rows = true word, shares of that word (each row sums to 100%).
  python3 scripts/make_confusion_final28.py research/figures_v3/fig13_confusion_final28.png [base|dann]
"""
import sys, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for fam in ("TH Sarabun New", "Thonburi", "Sukhumvit Set"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

which = sys.argv[2] if len(sys.argv) > 2 else "base"
rows = list(csv.DictReader(open(f"research/loso_final28/oof_{which}.csv", encoding="utf-8-sig")))
words = sorted({r["true"] for r in rows})
idx = {w: i for i, w in enumerate(words)}
n = len(words)
M = np.zeros((n, n))
for r in rows:
    M[idx[r["true"]], idx[r["pred"]]] += 1
acc_w = np.diag(M) / M.sum(1)
order = np.argsort(-acc_w)            # best word first
words = [words[i] for i in order]
M = M[np.ix_(order, order)]
P = M / M.sum(1, keepdims=True) * 100
acc = np.trace(M) / M.sum() * 100

fig, ax = plt.subplots(figsize=(8.2, 7.6), dpi=240, facecolor="white")
im = ax.imshow(P, cmap="Blues", vmin=0, vmax=100)
ax.set_xticks(range(n)); ax.set_yticks(range(n))
ax.set_xticklabels(words, rotation=90, fontsize=9.5)
ax.set_yticklabels(words, fontsize=9.5)
ax.set_xlabel("คำที่ระบบตอบ", fontsize=13)
ax.set_ylabel("คำที่ผู้แสดงทำจริง", fontsize=13)
for i in range(n):
    for j in range(n):
        v = P[i, j]
        if v >= 10 or (i == j):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.6,
                    color="white" if v > 55 else "#1F2937")
ax.set_title(f"ตารางความสับสน 28 คำ (กันผู้แสดงทีละคน, {int(M.sum()):,} ท่า)", fontsize=13, pad=10)
fig.text(0.01, 0.005, f"คำตอบเฉลี่ยจาก 3 ค่าเริ่มต้น รวมทุกท่าถูก {acc:.1f}% (ไม่ใช่ตัวเลข 51.9% ซึ่งเฉลี่ยรายผู้แสดง ผู้แสดง S01 และ S03 มีท่ามากสุด) เรียงจากคำที่ถูกมากไปน้อย", fontsize=7.5, color="#4B5563")
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("% ของคำที่ทำจริง", fontsize=10)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(sys.argv[1], facecolor="white")
print("saved", sys.argv[1], f"pooled accuracy {acc:.1f}%")
# biggest confusions
off = [(P[i, j], M[i, j], words[i], words[j]) for i in range(n) for j in range(n) if i != j]
for p, c, a, b in sorted(off, reverse=True)[:8]:
    print(f"  {a} -> {b}: {p:.0f}% ({int(c)} signs)")
