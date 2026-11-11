# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""RESULT panel cards, first-glance style, Thai + English. Numbers: report_th.md 4.3 and 4.5 (tables), loso_final28/summary.md.
 fig6r  random split vs unseen signer (84.8 vs 51.9)
 fig3r  left-right hand handling (13 words, S01-S03 held out)
 fig2r  per-word accuracy in three buckets (28 words, plain LSTM, pooled over held-out signers)
  python3 scripts/make_result_cards.py research/figures_v3
"""
import sys, os, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

G, A, R, GRAY, INK, MUTED = "#2E7D5B", "#E0A030", "#B5483A", "#C8CCD4", "#1F2937", "#4B5563"
out = sys.argv[1]
def font(en): plt.rcParams["font.family"] = ["Helvetica", "TH Sarabun New"] if en else "TH Sarabun New"

def fig6r(lang):
    en = lang == "en"; font(en); k = 0.8 if en else 1.0
    T = dict(title="A random split overstates accuracy by 33 points" if en else "การแบ่งแบบสุ่มทำให้ผลดูดีเกินจริง 33 จุด",
             l1="Random split\n(all signers mixed)" if en else "แบ่งสุ่ม 80/20\n(ผู้แสดงปนกัน)", l2="Leave one signer out\n(a signer never seen)" if en else "กันผู้แสดงทีละคน\n(คนที่ไม่เคยเห็น)",
             gap="33 points" if en else "ต่างกัน 33 จุด", dots="each dot = one signer" if en else "แต่ละจุด = ผู้แสดงหนึ่งคน",
             foot="28 words, plain LSTM. Random split: mean ± SD of repeated splits. Held-out: mean over 5 signers." if en else "28 คำ LSTM ปกติ แบ่งสุ่ม: ค่าเฉลี่ย ± ส่วนเบี่ยงเบนมาตรฐาน กันผู้แสดง: ค่าเฉลี่ยของผู้แสดง 5 คน")
    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=220, facecolor="white")
    ax.set_xlim(-0.6, 2.4); ax.set_ylim(0, 128); ax.axis("off")
    ax.text(-0.6, 122, T["title"], fontsize=21 * k, color=INK, fontweight="bold", va="center")
    ax.bar([0], [84.8], width=0.8, color=GRAY); ax.bar([1.4], [51.9], width=0.8, color=G)
    ax.errorbar([0], [84.8], yerr=[6.8], color=INK, capsize=7, lw=2.2)
    ax.text(0, 95, "84.8%", ha="center", fontsize=40 * k, color=INK, fontweight="bold")
    ax.text(1.4, 16, "51.9%", ha="center", fontsize=40 * k, color="white", fontweight="bold")
    for v in (59.1, 64.3, 51.5, 37.0, 47.6): ax.scatter([1.4 + 0.18 * (1 if v in (59.1, 51.5, 47.6) else -1)], [v], s=70, facecolor="white", edgecolor="#14532d", lw=1.8, zorder=5)
    ax.text(1.85, 30, T["dots"], ha="left", fontsize=12.5 * k, color=MUTED)
    ax.plot([0.4, 1.0], [84.8, 84.8], color=R, lw=2, ls=(0, (4, 3)))
    ax.add_patch(FancyArrowPatch((1.0, 84.8), (1.0, 52), arrowstyle="<|-|>", mutation_scale=18, color=R, lw=2.6))
    ax.plot([1.0, 1.0], [52, 52], color=R)
    ax.text(0.96, 68, T["gap"], ha="right", va="center", fontsize=20 * k, color=R, fontweight="bold")
    ax.text(0, -5, T["l1"], ha="center", va="top", fontsize=14 * k, color=INK, linespacing=1.25); ax.text(1.4, -5, T["l2"], ha="center", va="top", fontsize=14 * k, color=INK, linespacing=1.25)
    ax.plot([-0.5, 2.3], [0, 0], color=INK, lw=1.2)
    ax.text(-0.6, -22, T["foot"], fontsize=10.5 * k, color=MUTED, va="top")
    ax.set_ylim(-26, 128)
    fig.savefig(os.path.join(out, "fig6r_random_vs_unseen" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

def fig3r(lang):
    en = lang == "en"; font(en); k = 0.8 if en else 1.0
    T = dict(title="Handling left and right hands adds about 16 points" if en else "จัดการมือซ้าย–ขวา เพิ่มความแม่นยำราว 16 จุด",
             b=["No handling", "Flip during\ntraining", "Main hand moved\nto slot 1"] if en else ["ไม่จัดการ", "พลิกซ้ายขวา\nตอนฝึก", "ย้ายมือหลัก\nไปช่อง 1"],
             s2h="S02 alone" if en else "เฉพาะ S02", s2="35% to 74%" if en else "35% เป็น 74%",
             why="S02's main hand is in the other slot, so without handling the model misreads it" if en else "มือหลักของ S02 อยู่คนละช่องกับคนอื่น ถ้าไม่จัดการ โมเดลจะอ่านผิด",
             foot="13 words, mean accuracy on S01–S03 held out one at a time, 3 seeds. The two handling methods differ by 3.2 points, within the uncertainty." if en else "13 คำ ความแม่นยำเฉลี่ยเมื่อกัน S01–S03 ทีละคน 3 ค่าเริ่มต้น สองวิธีจัดการต่างกัน 3.2 จุด ซึ่งอยู่ในช่วงความไม่แน่นอน")
    fig, ax = plt.subplots(figsize=(10.4, 5.8), dpi=220, facecolor="white")
    ax.set_xlim(-0.6, 8.3); ax.set_ylim(-26, 112); ax.axis("off")
    ax.text(-0.6, 106, T["title"], fontsize=21 * k, color=INK, fontweight="bold", va="center")
    vals = [56.8, 72.7, 75.9]; cols = [R, G, "#1F6B4A"]; xs = [0, 1.6, 3.2]
    for x, v, c, l in zip(xs, vals, cols, T["b"]):
        ax.bar([x], [v], width=1.2, color=c); ax.text(x, v + 3, f"{v}%", ha="center", fontsize=30 * k, color=INK, fontweight="bold")
        ax.text(x, -4, l, ha="center", va="top", fontsize=14 * k, color=INK, linespacing=1.25)
    ax.plot([-0.7, 3.9], [0, 0], color=INK, lw=1.2)
    ax.add_patch(plt.Rectangle((4.5, 22), 3.7, 66, fc="#FDECEA", ec=R, lw=2))
    ax.text(6.35, 80, T["s2h"], ha="center", fontsize=17 * k, color=R, fontweight="bold")
    ax.text(6.35, 62, T["s2"], ha="center", fontsize=30 * k, color=INK, fontweight="bold")
    ax.text(6.35, 38, T["why"].replace(", so", ",\nso") if en else T["why"].replace(" ถ้าไม่จัดการ", "\nถ้าไม่จัดการ"), ha="center", va="center", fontsize=12.5 * k, color=MUTED, linespacing=1.3)
    ax.text(-0.6, -24, T["foot"], fontsize=10.5 * k, color=MUTED, va="top")
    fig.savefig(os.path.join(out, "fig3r_handedness" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

def fig2r(lang):
    en = lang == "en"; font(en); k = 0.8 if en else 1.0
    vocab = {w["th"]: w["en"] for w in json.load(open("scripts/vocab.json", encoding="utf-8"))["words"]}
    rows = []
    for line in open("research/loso_final28/summary.md", encoding="utf-8"):
        if line.startswith("| ") and "%" in line:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) == 3 and c[1].endswith("%"): rows.append((c[0], int(c[1][:-1])))
    assert len(rows) == 28, len(rows)
    rows.sort(key=lambda r: -r[1])
    buckets = [("≥ 75%", G, [r for r in rows if r[1] >= 75]), ("50–74%", A, [r for r in rows if 50 <= r[1] < 75]), ("< 50%", R, [r for r in rows if r[1] < 50])]
    n = [len(b[2]) for b in buckets]
    T = dict(title=f"28 words: {n[0]} above 75%, but {n[2]} below 50%" if en else f"28 คำ: {n[0]} คำแม่นเกิน 75% แต่ {n[2]} คำต่ำกว่า 50%",
             words="words" if en else "คำ",
             foot="Accuracy on signers the model never saw, plain LSTM, pooled over 5 held-out signers. “คุณ”" + (" (you)" if en else "") + " was tested on S04 and S05 only (50 clips), so its 100% should not be over-read." if en else "ความแม่นยำบนผู้แสดงที่โมเดลไม่เคยเห็น LSTM ปกติ รวมผู้แสดง 5 คน คำ “คุณ” ทดสอบเฉพาะ S04 และ S05 (50 คลิป) จึงไม่ควรตีความ 100% มากเกินไป")
    fig, ax = plt.subplots(figsize=(13, 6.4), dpi=200, facecolor="white")
    ax.set_xlim(0, 26); ax.set_ylim(-0.7, 11.6); ax.axis("off")
    ax.text(0, 11.0, T["title"], fontsize=23 * k, color=INK, fontweight="bold", va="center")
    cw, ch = 3.9, 0.9; x0 = 0
    for (name, col, items), cnt in zip(buckets, n):
        ax.text(x0, 9.7, f"{cnt}", fontsize=34 * k, color=col, fontweight="bold", va="center"); ax.text(x0 + 1.15, 9.55, f"{T['words']}  {name}", fontsize=17 * k, color=INK, va="center", fontweight="bold")
        per = 6
        for i, (w, v) in enumerate(items):
            c, r = divmod(i, per); x = x0 + c * (cw + 0.15); y = 8.5 - (r + 1) * 1.1
            ax.add_patch(FancyBboxPatch((x, y), cw, ch, boxstyle="round,pad=0,rounding_size=0.18", fc=col, ec="none", alpha=0.16))
            ax.add_patch(FancyBboxPatch((x, y), cw * v / 100, ch, boxstyle="round,pad=0,rounding_size=0.18", fc=col, ec="none", alpha=0.55)) if v > 0 else None
            label = f"{w}" + (f" ({vocab[w]})" if en else "")
            ax.text(x + 0.2, y + ch / 2, label, ha="left", va="center", fontsize=(12 if en else 15.5), color=INK, fontweight="bold")
            ax.text(x + cw - 0.15, y + ch / 2, f"{v}", ha="right", va="center", fontsize=15 * k, color=INK, fontweight="bold")
        x0 += (2 if len(items) > 6 else 1) * (cw + 0.15) + 0.5
    ax.text(0, -0.35, T["foot"], fontsize=11 * k if not en else 9.5, color=MUTED, va="center")
    fig.savefig(os.path.join(out, "fig2r_per_word" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

def per_word_run(run):
    d = {}
    on = False
    for line in open(f"research/{run}/summary.md", encoding="utf-8"):
        if line.startswith("## Per word"): on = True; continue
        if on and line.startswith("| ") and "%" in line:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 2 and c[1].endswith("%"): d[c[0]] = int(c[1][:-1])
        elif on and line.startswith("## "): break
    return d

def gloss():
    return {w["th"]: w["en"] for w in json.load(open("scripts/vocab.json", encoding="utf-8"))["words"]}

def fig4r(lang):
    en = lang == "en"; font(en); k = 0.8 if en else 1.0; gl = gloss()
    raw, rel = per_word_run("loso_setA"), per_word_run("loso_setA_head")
    words = sorted(raw, key=lambda w: rel[w] - raw[w], reverse=True)
    up = sum(rel[w] > raw[w] for w in words); down = sum(rel[w] < raw[w] for w in words); same = len(words) - up - down
    T = dict(title=f"Measuring the hand from the face: {up} words better, {down} worse" if en else f"วัดตำแหน่งมือจากใบหน้า: {up} คำดีขึ้น {down} คำแย่ลง",
             l1="raw picture coordinates" if en else "พิกัดดิบในภาพ", l2="relative to the face" if en else "สัมพัทธ์กับใบหน้า",
             foot="13 words, S01–S04 held out, plain LSTM, pooled. Mean over S01–S03: 72.7% to 78.6% (+5.9). Not adopted in the final model." if en else "13 คำ กัน S01–S04 ทีละคน LSTM ปกติ รวมผู้แสดง ค่าเฉลี่ย S01–S03: 72.7% เป็น 78.6% (+5.9) ยังไม่นำมาใช้ในแบบจำลองสุดท้าย")
    n = len(words)
    fig, ax = plt.subplots(figsize=(9.4, 7.2), dpi=220, facecolor="white")
    ax.set_xlim(-34, 112); ax.set_ylim(-3.2, n + 3.0); ax.axis("off")
    ax.text(-34, n + 2.2, T["title"], fontsize=20 * k, color=INK, fontweight="bold", va="center")
    ax.scatter([-30], [n + 0.9], s=90, color="#9CA3AF"); ax.text(-27, n + 0.9, T["l1"], va="center", fontsize=13 * k, color=MUTED)
    ax.scatter([20], [n + 0.9], s=90, color=G); ax.text(23, n + 0.9, T["l2"], va="center", fontsize=13 * k, color=MUTED)
    for i, w in enumerate(words):
        y = n - 1 - i; a, b = raw[w], rel[w]
        col = G if b > a else (R if b < a else "#9CA3AF")
        ax.text(-33, y, w + (f"  ({gl[w]})" if en else ""), ha="left", va="center", fontsize=(11 if en else 15), color=INK, fontweight="bold")
        ax.plot([a, b], [y, y], color=col, lw=3.2, alpha=0.9, zorder=2)
        ax.scatter([a], [y], s=70, color="#9CA3AF", zorder=3); ax.scatter([b], [y], s=90, color=col, zorder=4)
        if a == b:
            ax.text(a + 3, y, str(a), ha="left", va="center", fontsize=13 * k, color=MUTED, fontweight="bold")
        elif b >= a:
            ax.text(a - 2.2, y, str(a), ha="right", va="center", fontsize=12 * k, color=MUTED); ax.text(b + 2.5, y, str(b), ha="left", va="center", fontsize=14 * k, color=col, fontweight="bold")
        else:
            ax.text(a + 2.2, y, str(a), ha="left", va="center", fontsize=12 * k, color=MUTED); ax.text(b - 2.5, y, str(b), ha="right", va="center", fontsize=14 * k, color=col, fontweight="bold")
    ax.text(-34, -2.2, T["foot"], fontsize=10.5 * k, color=MUTED, va="center")
    fig.savefig(os.path.join(out, "fig4r_face_relative" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)
    return up, down, same

def fig13r(lang):
    import csv
    en = lang == "en"; font(en); k = 0.8 if en else 1.0; gl = gloss()
    rows = list(csv.DictReader(open("research/loso_final28/oof_base.csv", encoding="utf-8-sig")))
    words = sorted({r["true"] for r in rows}); ix = {w: i for i, w in enumerate(words)}; n = len(words)
    M = np.zeros((n, n))
    for r in rows: M[ix[r["true"]], ix[r["pred"]]] += 1
    order = np.argsort(-(np.diag(M) / M.sum(1))); words = [words[i] for i in order]; M = M[np.ix_(order, order)]
    P = M / M.sum(1, keepdims=True) * 100
    img = np.ones((n, n, 3))
    gcol, rcol = np.array([46, 125, 91]) / 255, np.array([181, 72, 58]) / 255
    for i in range(n):
        for j in range(n):
            a = min(1, P[i, j] / 100) if i == j else (min(1, 0.18 + P[i, j] / 55) if P[i, j] >= 4 else 0)
            img[i, j] = (1 - a) * np.ones(3) + a * (gcol if i == j else rcol)
    off = sorted(((P[i, j], int(M[i, j]), words[i], words[j], i, j) for i in range(n) for j in range(n) if i != j), reverse=True)[:6]
    T = dict(title="Which words get confused with which" if en else "คำไหนถูกสับสนกับคำไหน", sub="most common mix-ups (% of that word's signs)" if en else "ที่สับสนมากที่สุด (% ของท่าคำนั้น)",
             xl="word the system guessed" if en else "คำที่ระบบตอบ", yl="word actually signed" if en else "คำที่ทำจริง",
             leg1="correct" if en else "ตอบถูก", leg2="mix-up" if en else "สับสน",
             foot="28 words, plain LSTM, signers the model never saw (6,635 signs, 3 seeds averaged). Rows sorted from most to least accurate." if en else "28 คำ LSTM ปกติ ผู้แสดงที่โมเดลไม่เคยเห็น (6,635 ท่า เฉลี่ย 3 ค่าเริ่มต้น) แถวเรียงจากแม่นมากไปน้อย")
    fig = plt.figure(figsize=(14, 8.2), dpi=200, facecolor="white")
    fig.text(0.02, 0.955, T["title"], fontsize=24 * k, color=INK, fontweight="bold", va="center")
    ax = fig.add_axes([0.13, 0.19, 0.45, 0.70]); ax.imshow(img, interpolation="nearest")
    lab = lambda w: gl[w] if en else w
    ax.set_xticks(range(n)); ax.set_yticks(range(n)); ax.set_xticklabels([lab(w) for w in words], rotation=90, fontsize=(8.5 if en else 11)); ax.set_yticklabels([lab(w) for w in words], fontsize=(8.5 if en else 11))
    ax.tick_params(length=0); ax.set_xlabel(T["xl"], fontsize=14 * k); ax.set_ylabel(T["yl"], fontsize=14 * k)
    for sp in ax.spines.values(): sp.set_color("#D1D5DB")
    for v, c, a, b, i, j in off:
        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fc="none", ec=R, lw=2.6)); ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    # list of top mix-ups
    ax2 = fig.add_axes([0.63, 0.19, 0.35, 0.70]); ax2.set_xlim(0, 10); ax2.set_ylim(0, 8); ax2.axis("off")
    ax2.text(0, 7.6, T["sub"], fontsize=15 * k, color=MUTED, va="center")
    for r, (v, c, a, b, i, j) in enumerate(off):
        y = 6.4 - r * 1.08
        ax2.text(0, y + 0.25, f"{lab(a)}  to  {lab(b)}" if en else f"{a}  ถูกตอบเป็น  {b}", fontsize=(15 if en else 18) , color=INK, fontweight="bold", va="center")
        ax2.add_patch(FancyBboxPatch((0, y - 0.38), v / 60 * 8.0, 0.32, boxstyle="round,pad=0,rounding_size=0.08", fc=R, ec="none"))
        ax2.text(v / 60 * 8.0 + 0.2, y - 0.22, f"{v:.0f}%", fontsize=17 * k, color=R, fontweight="bold", va="center")
    fig.patches.append(FancyBboxPatch((0.64, 0.045), 0.012, 0.022, boxstyle="square,pad=0", fc=G, ec="none", transform=fig.transFigure, figure=fig)); fig.text(0.66, 0.056, T["leg1"], fontsize=13 * k, va="center", color=INK)
    fig.patches.append(FancyBboxPatch((0.74, 0.045), 0.012, 0.022, boxstyle="square,pad=0", fc=R, ec="none", transform=fig.transFigure, figure=fig)); fig.text(0.76, 0.056, T["leg2"], fontsize=13 * k, va="center", color=INK)
    fig.text(0.02, 0.018, T["foot"], fontsize=11 * k if not en else 9.5, color=MUTED, va="center")
    fig.savefig(os.path.join(out, "fig13r_confusion" + ("_en" if en else "") + ".png"), facecolor="white"); plt.close(fig)
    return [(a, b, round(v)) for v, c, a, b, i, j in off]

for lg in ("th", "en"): fig6r(lg); fig3r(lg); fig2r(lg); u = fig4r(lg); t6 = fig13r(lg)
print("face-relative up/down/same:", u); print("top mix-ups:", t6)
print("saved fig6r, fig3r, fig2r (th, en) in", out)
