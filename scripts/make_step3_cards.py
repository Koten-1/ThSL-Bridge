# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Step 3 (green) cards, read at a glance, Thai + English.
 fig16  the 5 leave-one-signer-out rounds (tested-sign counts: research/loso_final28/summary.md)
 fig20  horizontal flow: plain LSTM lane, and LSTM + DANN lane with the extra branch (report_th.md 3.3)
  python3 scripts/make_step3_cards.py research/figures_v3
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

G, GD, GL, INK, MUTED = "#5DBB5D", "#2F8F3A", "#DDF1DD", "#1F2937", "#4B5563"
out = sys.argv[1]
def setfont(en): plt.rcParams["font.family"] = "Helvetica" if en else "TH Sarabun New"

def fig16(lang):
    en = lang == "en"; setfont(en); k = 0.8 if en else 1.0
    T = dict(title="Leave one signer out: 5 rounds" if en else "กันผู้แสดงทีละคน: 5 รอบ",
             msg="Every round is tested on a signer the model has never seen" if en else "ทุกรอบทดสอบกับผู้แสดงที่โมเดลไม่เคยเห็น",
             rnd="Round" if en else "รอบ", test="TEST" if en else "ทดสอบ", cnt="signs tested" if en else "ท่าที่ทดสอบ",
             tr="trained on the other four" if en else "ฝึกจากอีกสี่คน", ts="tested on an unseen signer" if en else "ทดสอบกับคนที่ไม่เคยเห็น")
    signers = ["S01", "S02", "S03", "S04", "S05"]; tested = [2464, 993, 2409, 643, 126]
    fig, ax = plt.subplots(figsize=(8.6, 5.4), dpi=220, facecolor="white")
    ax.set_xlim(-1.7, 9.2); ax.set_ylim(-1.2, 7.0); ax.axis("off")
    ax.text(-1.6, 6.65, T["title"], fontsize=21 * k, color=INK, fontweight="bold", va="center")
    cw, ch, gx, gy = 1.15, 0.78, 0.08, 0.14
    for j, s in enumerate(signers):
        ax.text(j * (cw + gx) + cw / 2, 5.6, s, ha="center", fontsize=16 * k, color=INK, fontweight="bold")
    ax.text(5 * (cw + gx) + 0.45, 5.6, T["cnt"], ha="left", fontsize=13 * k, color=MUTED)
    for r in range(5):
        y = 4.55 - r * (ch + gy)
        ax.text(-0.2, y + ch / 2, f"{T['rnd']} {r + 1}", ha="right", va="center", fontsize=16 * k, color=INK)
        for j in range(5):
            test = j == r
            ax.add_patch(FancyBboxPatch((j * (cw + gx), y), cw, ch, boxstyle="round,pad=0,rounding_size=0.09", fc=GD if test else GL, ec="none"))
            if test: ax.text(j * (cw + gx) + cw / 2, y + ch / 2, T["test"], ha="center", va="center", fontsize=14 * k, color="white", fontweight="bold")
        ax.text(5 * (cw + gx) + 0.45, y + ch / 2, f"{tested[r]:,}", ha="left", va="center", fontsize=17 * k, color=INK, fontweight="bold")
    ax.add_patch(FancyBboxPatch((0, 0.1), 0.5, 0.36, boxstyle="round,pad=0,rounding_size=0.06", fc=GL, ec="none")); ax.text(0.65, 0.28, T["tr"], va="center", fontsize=13 * k, color=INK)
    ax.add_patch(FancyBboxPatch((4.0, 0.1), 0.5, 0.36, boxstyle="round,pad=0,rounding_size=0.06", fc=GD, ec="none")); ax.text(4.65, 0.28, T["ts"], va="center", fontsize=13 * k, color=INK)
    ax.text(-1.6, -0.7, T["msg"], fontsize=15 * k, color=GD, fontweight="bold", va="center")
    fig.savefig(os.path.join(out, "fig16_loso_rounds" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

def fig20(lang):
    en = lang == "en"; setfont(en); k = 0.8 if en else 1.0
    T = dict(title="Plain LSTM vs LSTM + DANN" if en else "LSTM ปกติ เทียบกับ LSTM + DANN",
             sub="Same data and settings; the only difference is one extra branch" if en else "ข้อมูลและการตั้งค่าเหมือนกัน ต่างกันที่หัวเสริมตัวเดียว",
             l1="Plain LSTM" if en else "LSTM ปกติ", l2="LSTM + DANN",
             A="Sign data\n30 × 126" if en else "ข้อมูลท่า\n30 × 126", B="LSTM\n2 layers" if en else "LSTM\n2 ชั้น",
             C="Word head" if en else "หัวจำแนกคำ", D="Predicted\nword" if en else "คำที่ทาย",
             grl="Gradient\nreversal" if en else "ตัวกลับทิศ", sg="Guesses\nthe signer" if en else "ทายผู้แสดง",
             add="Added by DANN · training only" if en else "ส่วนที่ DANN เพิ่ม · ใช้ตอนฝึกเท่านั้น",
             goal="Goal: make the LSTM\nforget who is signing" if en else "เป้าหมาย: ให้ LSTM\nลืมว่าใครเป็นผู้ทำท่า")
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=220, facecolor="white")
    ax.set_xlim(-0.2, 22); ax.set_ylim(-0.2, 11.4); ax.axis("off")
    ax.text(0, 11.0, T["title"], fontsize=21 * k, color=INK, fontweight="bold", va="center")
    ax.text(0, 10.2, T["sub"], fontsize=13.5 * k, color=MUTED, va="center")
    def box(x, y, w, h, t, solid=False, fs=15):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.2", fc=GD if solid else GL, ec=GD, lw=1.6))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs * k, color="white" if solid else INK, fontweight="bold" if solid else "normal", linespacing=1.2)
    def arr(p, q, col=MUTED, lw=2.0): ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, color=col, lw=lw))
    def lane(y, label):
        ax.text(0, y + 1.55, label, fontsize=15.5 * k, color=GD, fontweight="bold", va="center")
        box(0, y - 0.8, 3.7, 1.6, T["A"]); arr((3.75, y), (4.85, y))
        box(4.9, y - 0.8, 4.6, 1.6, T["B"]); arr((9.55, y), (10.65, y))
        box(10.7, y - 0.8, 4.5, 1.6, T["C"]); arr((15.25, y), (16.35, y))
        ax.add_patch(FancyBboxPatch((16.4, y - 0.8), 4.6, 1.6, boxstyle="round,pad=0,rounding_size=0.2", fc="#FFE066", ec="#C9A400", lw=1.6))
        ax.text(18.7, y, T["D"], ha="center", va="center", fontsize=15 * k, color=INK, fontweight="bold", linespacing=1.2)
    lane(8.0, T["l1"])
    ax.plot([5.2, 21], [6.1, 6.1], color="#E3E7EE", lw=1.5)
    lane(4.5, T["l2"])
    # DANN branch (dashed region, solid boxes)
    ax.add_patch(FancyBboxPatch((8.6, -0.1), 12.4, 2.75, boxstyle="round,pad=0,rounding_size=0.25", fc="none", ec=GD, lw=1.8, ls=(0, (5, 3))))
    ax.text(14.8, 2.3, T["add"], ha="center", va="center", fontsize=12.5 * k, color=GD, fontweight="bold")
    ax.plot([7.2, 7.2, 9.35], [3.7, 0.9, 0.9], color=GD, lw=2.0)
    arr((9.0, 0.9), (9.45, 0.9), col=GD)
    box(9.5, 0.1, 4.2, 1.6, T["grl"], solid=True, fs=14)
    arr((13.75, 0.9), (15.35, 0.9), col=GD)
    box(15.4, 0.1, 4.8, 1.6, T["sg"], solid=True, fs=14)
    ax.text(0, 1.6, T["goal"], fontsize=13.5 * k, color=INK, va="center", linespacing=1.3)
    fig.savefig(os.path.join(out, "fig20_dann_card" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

def fig16r(lang):
    """RESULT version: each test cell -> arrow -> accuracy on that signer (plain LSTM vs LSTM + DANN). Numbers: loso_final28/summary.md"""
    en = lang == "en"; setfont(en); k = 0.8 if en else 1.0
    plain = [59.1, 64.3, 51.5, 37.0, 47.6]; dann = [52.6, 58.1, 46.9, 36.2, 37.8]
    T = dict(title="Result on a signer the model has never seen" if en else "ผลเมื่อทดสอบกับผู้แสดงที่โมเดลไม่เคยเห็น",
             rnd="Round" if en else "รอบ", test="TEST" if en else "ทดสอบ", pl="Plain LSTM" if en else "LSTM ปกติ", da="LSTM + DANN",
             mean="Mean" if en else "เฉลี่ย", msg="DANN is lower for all 5 signers (mean 46.3 vs 51.9)" if en else "DANN ต่ำกว่าในผู้แสดงทั้ง 5 คน (เฉลี่ย 46.3 เทียบ 51.9)",
             acc="accuracy on the test signer (%)" if en else "ความแม่นยำบนผู้แสดงที่ทดสอบ (%)")
    signers = ["S01", "S02", "S03", "S04", "S05"]
    fig, ax = plt.subplots(figsize=(10.6, 6.0), dpi=220, facecolor="white")
    ax.set_xlim(-1.7, 13.4); ax.set_ylim(-1.6, 7.0); ax.axis("off")
    ax.text(-1.6, 6.65, T["title"], fontsize=21 * k, color=INK, fontweight="bold", va="center")
    cw, ch, gx, step = 1.0, 0.78, 0.07, 0.92
    for j, s_ in enumerate(signers): ax.text(j * (cw + gx) + cw / 2, 5.62, s_, ha="center", fontsize=15 * k, color=INK, fontweight="bold")
    x0 = 7.7
    ax.add_patch(FancyBboxPatch((x0, 5.52), 0.5, 0.3, boxstyle="round,pad=0,rounding_size=0.05", fc=GD, ec="none")); ax.text(x0 + 0.62, 5.67, T["pl"], va="center", fontsize=13.5 * k, color=INK)
    ax.add_patch(FancyBboxPatch((x0 + 3.0, 5.52), 0.5, 0.3, boxstyle="round,pad=0,rounding_size=0.05", fc="#A9D6A9", ec="none")); ax.text(x0 + 3.62, 5.67, T["da"], va="center", fontsize=13.5 * k, color=INK)
    sc = 0.04
    for r in range(5):
        y = 4.55 - r * step
        ax.text(-0.15, y + ch / 2, f"{T['rnd']} {r + 1}", ha="right", va="center", fontsize=15 * k, color=INK)
        for j in range(5):
            test = j == r
            ax.add_patch(FancyBboxPatch((j * (cw + gx), y), cw, ch, boxstyle="round,pad=0,rounding_size=0.09", fc=GD if test else GL, ec="none"))
            if test: ax.text(j * (cw + gx) + cw / 2, y + ch / 2, T["test"], ha="center", va="center", fontsize=12.5 * k, color="white", fontweight="bold")
        ax.add_patch(FancyArrowPatch((5 * (cw + gx) + 0.1, y + ch / 2), (x0 - 0.2, y + ch / 2), arrowstyle="-|>", mutation_scale=15, color=MUTED, lw=1.8))
        for v, yy, col, bold in ((plain[r], y + 0.42, GD, True), (dann[r], y + 0.02, "#A9D6A9", False)):
            ax.add_patch(FancyBboxPatch((x0, yy), v * sc * 1.0, 0.34, boxstyle="round,pad=0,rounding_size=0.04", fc=col, ec="none"))
            ax.text(x0 + v * sc + 0.1, yy + 0.17, f"{v:.1f}", va="center", fontsize=13.5 * k, color=INK, fontweight="bold" if bold else "normal")
    ym = -0.45
    ax.plot([-1.5, 13.0], [ym + 0.95, ym + 0.95], color="#E3E7EE", lw=1.4)
    ax.text(5.9, ym + 0.35, T["mean"], ha="right", va="center", fontsize=16 * k, color=INK, fontweight="bold")
    ax.add_patch(FancyArrowPatch((6.15, ym + 0.35), (x0 - 0.2, ym + 0.35), arrowstyle="-|>", mutation_scale=15, color=MUTED, lw=1.8))
    for v, yy, col in ((51.9, ym + 0.42, GD), (46.3, ym + 0.02, "#A9D6A9")):
        ax.add_patch(FancyBboxPatch((x0, yy), v * sc, 0.34, boxstyle="round,pad=0,rounding_size=0.04", fc=col, ec="none"))
        ax.text(x0 + v * sc + 0.1, yy + 0.17, f"{v}", va="center", fontsize=15 * k, color=INK, fontweight="bold")
    ax.text(x0, 6.3, T["acc"], fontsize=12 * k, color=MUTED, va="center")
    ax.text(-1.6, -1.35, T["msg"], fontsize=16 * k, color=GD, fontweight="bold", va="center")
    fig.savefig(os.path.join(out, "fig16r_loso_result" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.12); plt.close(fig)

for lg in ("th", "en"): fig16(lg); fig16r(lg); fig20(lg)
print("saved fig16 + fig20 (th, en) in", out)
