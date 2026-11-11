# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Redraw the two slide charts whose Thai word labels were garbled (stacked vowel + tone marks lost by matplotlib's default Thai font):
  fig2_per_word_heldout.png   per-word accuracy on unseen signers, 28 words        (research/loso_final28/summary.md)
  fig4_face_relative.png      raw picture coordinates vs face-relative, 13 words   (research/loso_setA, research/loso_setA_head)
Uses the 'Sukhumvit Set' font, which keeps the marks. Numbers are read from the summary files, nothing is typed by hand.
  python3 scripts/make_thai_figures.py OUT_DIR
"""
import re, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for fam in ("Sukhumvit Set", "Krungthep", "TH Sarabun New"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
plt.rcParams["axes.unicode_minus"] = False

R = Path(__file__).resolve().parent.parent / "research"
GREEN, AMBER, RED, BLUE, ORANGE = "#2E7D5B", "#C9801A", "#B5483A", "#2B5F8E", "#C9801A"


def per_word(run):
    out, on = {}, False
    for line in (R / run / "summary.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| word |"):
            on = True; continue
        if on and line.startswith("|---"):
            continue
        if on:
            m = re.match(r"\| (\S+) \| (\d+)%", line)
            if not m:
                break
            out[m.group(1)] = int(m.group(2))
    return out


def fig2(out):
    d = per_word("loso_final28")
    items = sorted(d.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(6.6, 6.5), dpi=200)
    cols = [GREEN if v >= 75 else AMBER if v >= 50 else RED for _, v in items]
    ax.barh([w for w, _ in items], [v for _, v in items], color=cols, height=0.8)
    for i, (w, v) in enumerate(items):
        ax.text(v + 1.2, i, f"{v}", va="center", fontsize=7.5, color="#1F2937")
    ax.set_xlim(0, 112); ax.set_xlabel("ความแม่นยำบนผู้แสดงที่แบบจำลองไม่เคยเห็น (%)", fontsize=11)
    ax.set_title("ความแม่นยำรายคำ (28 คำ กันผู้แสดงทีละคน)\nเขียว ≥ 75%  เหลือง 50–74%  แดง < 50%", fontsize=12.5)
    ax.tick_params(axis="y", labelsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.02, 0.005, "* คำ \"คุณ\" ทดสอบเฉพาะผู้แสดง S04 และ S05 (50 คลิป) จึง 100% ไม่ควรตีความ", fontsize=8.5, color="#4B5563")
    fig.tight_layout(rect=(0, 0.02, 1, 1)); fig.savefig(out / "fig2_per_word_heldout.png", facecolor="white"); plt.close(fig)


def fig4(out):
    raw, rel = per_word("loso_setA"), per_word("loso_setA_head")
    words = sorted(raw, key=lambda w: rel[w] - raw[w])
    fig, ax = plt.subplots(figsize=(6.8, 4.9), dpi=200)
    for i, w in enumerate(words):
        ax.plot([raw[w], rel[w]], [i, i], color="#9CA3AF", lw=1.4, zorder=1)
    ax.scatter([raw[w] for w in words], range(len(words)), color=ORANGE, s=34, zorder=2, label="พิกัดดิบในภาพ")
    ax.scatter([rel[w] for w in words], range(len(words)), color=GREEN, s=34, zorder=3, label="สัมพัทธ์กับใบหน้า")
    ax.set_yticks(range(len(words))); ax.set_yticklabels(words, fontsize=11)
    ax.set_xlim(-4, 106); ax.set_xlabel("ความแม่นยำบนผู้แสดงที่ถูกกัน (%)", fontsize=11)
    ax.set_title("ตำแหน่งมือสัมพัทธ์กับใบหน้า (13 คำ ผู้แสดง S01 ถึง S04)\nบางคำดีขึ้นมาก บางคำแย่ลง", fontsize=12.5)
    ax.legend(loc="lower left", fontsize=9.5, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig4_face_relative.png", facecolor="white"); plt.close(fig)


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    fig2(out); fig4(out); print("saved to", out)
