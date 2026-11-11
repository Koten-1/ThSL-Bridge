# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Step 4 cards (answer or "not sure"), pink accent.
 fig25  concept: a per-word confidence threshold (example numbers are illustrative)
 fig26  evidence: what the threshold promised vs what a NEW signer got (report_th.md table 6, section 4.7)
  python3 scripts/make_step4_cards.py research/figures_v3
Writes fig25_threshold_{th,en}.png and fig26_threshold_evidence_{th,en}.png
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

PINK, PINKF, GREEN, GREENF, INK, MUTED, GRAY = "#E0559E", "#FBE3EF", "#3DA35D", "#E0F2E6", "#1F2937", "#4B5563", "#C9CDD6"
out = sys.argv[1]
TXT = {
 "th": dict(font="TH Sarabun New", fs=1.0,
   t25="ตอบหรือไม่แน่ใจ: เกณฑ์ความเชื่อมั่นรายคำ", s25="โมเดลให้คะแนนความมั่นใจของแต่ละคำ ถ้าไม่ถึงเกณฑ์ของคำนั้น จะไม่ตอบ",
   axis="ความมั่นใจของโมเดล", low="ต่ำ", high="สูง", thr="เกณฑ์ของคำนั้น", show="แสดงคำ", unsure="ไม่แน่ใจ",
   w1="ช่วย", w2="ขอบคุณ", note="เกณฑ์ตั้งแยกรายคำ ให้คำตอบที่รับแม่นอย่างน้อย 90% · ตัวเลข 41% และ 92% ในภาพเป็นตัวอย่าง",
   t26="เกณฑ์ที่ตั้งไว้ เทียบกับที่ได้จริงกับผู้แสดงใหม่", ylab="ความแม่นยำของคำตอบที่ระบบยอมตอบ (%)",
   b=["ที่เกณฑ์สัญญาไว้\n(ตั้งจากการแบ่งสุ่ม)", "ที่ได้จริง\nกับผู้แสดงใหม่", "ตั้งจากผู้แสดง\nคนอื่น"],
   ans=["ตอบ 92% ของท่า", "ตอบ 72%", "ตอบ 47%"], target="เป้า 90%", foot="ผู้แสดงที่ไม่เคยเห็น 5 คน (6,635 ท่า) · เฉลี่ยจากแบบจำลอง 3 ตัว"),
 "en": dict(font="Helvetica", fs=0.82,
   t25="Answer or \"not sure\": a confidence threshold per word", s25="The model scores its confidence for each word; below that word's threshold it does not answer",
   axis="Model confidence", low="low", high="high", thr="threshold for that word", show="show the word", unsure="not sure",
   w1="help", w2="thank you", note="Each word's threshold is set so accepted answers are at least 90% accurate · 41% and 92% are example values",
   t26="What the threshold promised vs what a new signer got", ylab="Accuracy of the answers the system accepts (%)",
   b=["Promised\n(threshold from\nrandom split)", "Actual on\na new signer", "Threshold set from\nother signers"],
   ans=["answers 92% of signs", "answers 72%", "answers 47%"], target="target 90%", foot="Unseen signers, 5 people (6,635 signs) · average of 3 models"),
}

def fig25(lang):
    T = TXT[lang]; plt.rcParams["font.family"] = T["font"]; k = T["fs"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6), dpi=220, facecolor="white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
    ax.text(0, 5.95, T["t25"], fontsize=16.5 * k, color=INK, fontweight="bold", va="center")
    ax.text(0, 5.38, T["s25"], fontsize=12 * k, color=MUTED, va="center")
    thr = 5.8
    ax.add_patch(FancyBboxPatch((0.4, 2.55), thr - 0.4, 0.75, boxstyle="round,pad=0,rounding_size=0.12", fc=PINKF, ec="none"))
    ax.add_patch(FancyBboxPatch((thr, 2.55), 9.6 - thr, 0.75, boxstyle="round,pad=0,rounding_size=0.12", fc=GREENF, ec="none"))
    ax.plot([thr, thr], [2.35, 3.5], color=PINK, lw=2.4, ls=(0, (4, 2.5)))
    ax.text(thr, 3.72, T["thr"], ha="center", fontsize=12.5 * k, color=PINK, fontweight="bold")
    ax.text(0.4, 2.1, T["low"], fontsize=11.5 * k, color=MUTED, va="center"); ax.text(9.6, 2.1, T["high"], fontsize=11.5 * k, color=MUTED, va="center", ha="right")
    ax.text(5.0, 2.1, T["axis"], fontsize=11.5 * k, color=MUTED, va="center", ha="center")
    # two example words
    for x, w, pct, col, fc in ((2.7, T["w1"], "41%", PINK, "#FFFFFF"), (7.7, T["w2"], "92%", GREEN, "#FFFFFF")):
        ax.add_patch(FancyBboxPatch((x - 1.3, 4.15), 2.6, 0.8, boxstyle="round,pad=0,rounding_size=0.15", fc=fc, ec=col, lw=1.8))
        ax.text(x, 4.55, f"{w}  {pct}", ha="center", va="center", fontsize=14 * k, color=INK, fontweight="bold")
        ax.add_patch(FancyArrowPatch((x, 4.1), (x, 3.38), arrowstyle="-|>", mutation_scale=13, color=col, lw=1.8))
    ax.add_patch(FancyBboxPatch((1.0, 0.85), 3.4, 0.8, boxstyle="round,pad=0,rounding_size=0.15", fc="#E5E7EB", ec="#9CA3AF", lw=1.4))
    ax.text(2.7, 1.25, T["unsure"], ha="center", va="center", fontsize=15 * k, color=MUTED, fontweight="bold")
    ax.add_patch(FancyBboxPatch((5.5, 0.85), 4.4, 0.8, boxstyle="round,pad=0,rounding_size=0.15", fc="#FFE066", ec="#C9A400", lw=1.4))
    ax.text(7.7, 1.25, T["show"] + ": " + T["w2"], ha="center", va="center", fontsize=14 * k, color=INK, fontweight="bold")
    ax.text(5.0, 0.3, T["note"], ha="center", fontsize=10.5 * k, color=MUTED)
    fig.savefig(os.path.join(out, f"fig25_threshold_{lang}.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

def fig26(lang):
    T = TXT[lang]; plt.rcParams["font.family"] = T["font"]; k = T["fs"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6), dpi=220, facecolor="white")
    vals = [95.4, 66.2, 76.7]; cols = [GRAY, PINK, "#EE93BF"]
    bars = ax.bar(range(3), vals, color=cols, width=0.58, zorder=3)
    for i, v in enumerate(vals):
        ax.text(i, v + 1.6, f"{v:.1f}%", ha="center", fontsize=16 * k, color=INK, fontweight="bold")
        ax.text(i, 5, T["ans"][i], ha="center", fontsize=11 * k, color="white" if i else INK, zorder=5)
    ax.axhline(90, color=GREEN, lw=1.8, ls=(0, (5, 3)), zorder=2)
    ax.text(2.45, 91.5, T["target"], ha="right", fontsize=12.5 * k, color=GREEN, fontweight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels(T["b"], fontsize=12 * k); ax.set_ylim(0, 108)
    ax.set_ylabel(T["ylab"], fontsize=11.5 * k); ax.tick_params(axis="y", labelsize=11 * k)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_title(T["t26"], fontsize=16.5 * k, color=INK, loc="left", fontweight="bold", pad=12)
    ax.set_xlabel(T["foot"], fontsize=10.5 * k, color=MUTED, labelpad=16)
    fig.savefig(os.path.join(out, f"fig26_threshold_evidence_{lang}.png"), facecolor="white", bbox_inches="tight", pad_inches=0.15); plt.close(fig)

for lg in ("th", "en"): fig25(lg); fig26(lg)
print("saved fig25/fig26 th+en in", out)
