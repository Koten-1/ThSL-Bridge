# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Two flow charts for the poster.
 fig22  data collection workflow (stage 1, orange): facts from the dataset card, scripts/vocab.json, make_recording_flow.py
 fig23  system overview: sign -> word (5 steps, blue) and speech/text -> sign clip (report_th.md 3.1)
  python3 scripts/make_workflows.py research/figures_v3
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

for fam in ("TH Sarabun New", "Thonburi"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam; break
INK, MUTED = "#1F2937", "#4B5563"
OR, ORF, ORD = "#F0953A", "#FDEBD6", "#C9701A"
BL, BLF = "#2B5F8E", "#E3ECF6"
out = sys.argv[1]

def box(ax, cx, cy, w, h, text, fc, ec, fs=13, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.15", fc=fc, ec=ec, lw=1.6))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.25, fontweight="bold" if bold else "normal")

def arr(ax, p, q, col=INK, lw=1.8):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, color=col, lw=lw))

def fig22(lang="th"):
    en = lang == "en"
    plt.rcParams["font.family"] = "Helvetica" if en else "TH Sarabun New"
    k = 0.82 if en else 1.0
    T = dict(
      title="Data collection: how the signs were recorded" if en else "การเก็บข้อมูล: ขั้นตอนการบันทึก",
      b1="Words chosen with the deaf club\n5 deaf signers gave written consent" if en else "เลือกคำร่วมกับชมรมฯ\nผู้แสดงหูหนวก 5 คนลงนามยินยอม",
      b2="Record with a smartphone" if en else "บันทึกด้วยสมาร์ตโฟน",
      per="Per word\n(30 words)" if en else "ต่อ 1 คำ\n(30 คำ)",
      b3="Signer repeats the sign\nfor that one word" if en else "ผู้แสดงทำท่าของคำนั้นซ้ำ ๆ",
      b4="Each sign saved as a short video\n(median length 2.4 s)" if en else "บันทึกเป็นวิดีโอสั้น\n(ความยาวมัธยฐาน 2.4 วินาที)",
      rep="repeat\n~100\ntimes" if en else "ทำซ้ำ\nราว 100\nครั้ง",
      cnt="S01–S03: about 75–105 per word · S04–S05: 5–46 per word" if en else "S01–S03 ราว 75–105 ครั้งต่อคำ · S04–S05 คำละ 5–46 ครั้ง",
      nos="No fixed script for how to sign" if en else "ไม่มีสคริปต์ตายตัวว่าต้องทำท่าอย่างไร",
      done="All words done" if en else "ครบทุกคำ",
      b5="Files named with signer codes (S01…)\nOriginal videos stay with the team" if en else "ตั้งชื่อไฟล์ด้วยรหัสผู้แสดง (S01…)\nวิดีโอต้นฉบับเก็บไว้กับทีม",
      end="7,267 videos" if en else "ได้วิดีโอ 7,267 ไฟล์")
    fig, ax = plt.subplots(figsize=(6.4, 7.9), dpi=220, facecolor="white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 12.6); ax.axis("off")
    ax.text(0, 12.3, T["title"], fontsize=17 * (0.9 if en else 1), color=INK, fontweight="bold", va="center")
    cx, w = 3.7, 6.0
    box(ax, cx, 11.0, w, 1.1, T["b1"], ORF, OR, fs=13 * k)
    arr(ax, (cx, 10.4), (cx, 9.9))
    box(ax, cx, 9.35, w, 0.95, T["b2"], ORF, OR, fs=13 * k)
    ax.add_patch(Rectangle((0.3, 3.5), 7.9, 5.3, fc="none", ec=ORD, lw=1.6, ls=(0, (5, 3))))
    ax.text(8.45, 8.45, T["per"], fontsize=12.5 * k, color=ORD, fontweight="bold", va="top", ha="left")
    arr(ax, (cx, 8.85), (cx, 8.35))
    box(ax, cx, 7.65, w - 0.8, 1.15, T["b3"], ORF, OR, fs=13 * k)
    arr(ax, (cx, 7.05), (cx, 6.55))
    box(ax, cx, 5.7, w - 0.8, 1.4, T["b4"], ORF, OR, fs=13 * k)
    xr = cx + (w - 0.8) / 2
    ax.plot([xr, 6.85, 6.85], [5.7, 5.7, 7.65], color=ORD, lw=1.8)
    arr(ax, (6.85, 7.65), (xr + 0.03, 7.65), col=ORD)
    ax.text(6.98, 6.7, T["rep"], fontsize=11.5 * k, color=ORD, ha="left", va="center")
    ax.text(cx, 4.45, T["cnt"], fontsize=10.5 * k, color=MUTED, ha="center", va="center")
    ax.text(cx, 3.85, T["nos"], fontsize=11 * k, color=ORD, ha="center", va="center", fontweight="bold")
    arr(ax, (cx, 3.5), (cx, 2.65))
    ax.text(cx + 0.2, 3.07, T["done"], fontsize=11.5 * k, color=INK, ha="left", va="center")
    box(ax, cx, 1.95, w, 1.25, T["b5"], ORF, OR, fs=13 * k)
    arr(ax, (cx, 1.3), (cx, 0.8))
    box(ax, cx, 0.4, w, 0.75, T["end"], OR, OR, bold=True, fs=13.5 * k)
    ax.texts[-1].set_color("white")
    fig.savefig(os.path.join(out, "fig22_collection_workflow" + ("_en" if en else "") + ".png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

def fig23():
    fig, ax = plt.subplots(figsize=(12, 5.6), dpi=200, facecolor="white")
    ax.set_xlim(-0.2, 20); ax.set_ylim(0, 9.4); ax.axis("off")
    ax.text(0, 9.1, "ภาพรวมระบบ ThSL Bridge", fontsize=19, color=INK, fontweight="bold", va="center")
    ax.text(0, 8.45, "ภาพจากกล้องถูกประมวลผลในเครื่องผู้ใช้", fontsize=13, color=MUTED, va="center")
    # direction 1
    ax.text(0, 7.7, "ทิศที่ 1  จากภาษามือเป็นข้อความและเสียง", fontsize=14.5, color=BL, fontweight="bold", va="center")
    steps = [("1", "ผู้ใช้ทำท่า", "หน้ากล้อง\nเว็บแคมหรือมือถือ"),
             ("2", "หาจุดมือ", "MediaPipe หา 21 จุดต่อมือ\nเป็น 126 ค่าต่อเฟรม"),
             ("3", "ตัดท่า", "เริ่มเมื่อมือขยับ จบเมื่อนิ่ง\nย่อเหลือ 30 เฟรม"),
             ("4", "จำแนกคำ", "LSTM ทายคำ\nจากข้อมูล 30 เฟรม"),
             ("5", "ตอบหรือปฏิเสธ", "ถึงเกณฑ์ความเชื่อมั่น: แสดงคำ\nไม่ถึง: บอกว่า \"ไม่แน่ใจ\"")]
    bw, gap, x0 = 3.45, 0.62, 0.0
    for i, (n, t, d) in enumerate(steps):
        x = x0 + i * (bw + gap)
        ax.add_patch(FancyBboxPatch((x, 5.45), bw, 1.5, boxstyle="round,pad=0,rounding_size=0.15", fc=BLF, ec=BL, lw=1.6))
        ax.add_patch(Circle((x + 0.42, 6.2), 0.3, fc=BL, ec="none"))
        ax.text(x + 0.42, 6.2, n, ha="center", va="center", fontsize=14, color="white", fontweight="bold")
        ax.text(x + 0.9, 6.2, t, ha="left", va="center", fontsize=15, color=INK, fontweight="bold")
        ax.text(x + bw / 2, 4.75, d, ha="center", va="center", fontsize=11.8, color=MUTED, linespacing=1.3)
        if i < 4:
            arr(ax, (x + bw + 0.04, 6.2), (x + bw + gap - 0.04, 6.2), col=BL)
    # direction 2
    ax.text(0, 3.25, "ทิศที่ 2  จากเสียงหรือข้อความเป็นภาษามือ", fontsize=14.5, color="#2E7D5B", fontweight="bold", va="center")
    steps2 = [("1", "พูดหรือพิมพ์", "ผู้ใช้ทั่วไปพูดหรือพิมพ์ภาษาไทย"),
              ("2", "ตัดคำ", "แยกประโยคเป็นคำ"),
              ("3", "ค้นในรายการคำ", "เทียบกับคำที่ระบบรองรับ"),
              ("4", "แสดงท่า", "แสดงคลิปหรือลิงก์พจนานุกรม\nถ้าไม่มีคำนั้น จะแจ้งให้ทราบ")]
    bw2, gap2 = 4.3, 0.75
    for i, (n, t, d) in enumerate(steps2):
        x = i * (bw2 + gap2)
        ax.add_patch(FancyBboxPatch((x, 1.45), bw2, 1.2, boxstyle="round,pad=0,rounding_size=0.15", fc="#E4F2EA", ec="#2E7D5B", lw=1.6))
        ax.add_patch(Circle((x + 0.42, 2.05), 0.28, fc="#2E7D5B", ec="none"))
        ax.text(x + 0.42, 2.05, n, ha="center", va="center", fontsize=13, color="white", fontweight="bold")
        ax.text(x + 0.9, 2.05, t, ha="left", va="center", fontsize=14.5, color=INK, fontweight="bold")
        ax.text(x + bw2 / 2, 0.8, d, ha="center", va="center", fontsize=11.8, color=MUTED, linespacing=1.3)
        if i < 3:
            arr(ax, (x + bw2 + 0.04, 2.05), (x + bw2 + gap2 - 0.04, 2.05), col="#2E7D5B")
    fig.savefig(os.path.join(out, "fig23_system_overview.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

def fig23_en():
    plt.rcParams["font.family"] = "Helvetica"
    fig, ax = plt.subplots(figsize=(12, 5.6), dpi=200, facecolor="white")
    ax.set_xlim(-0.2, 20.4); ax.set_ylim(0, 9.4); ax.axis("off")
    ax.text(0, 9.1, "ThSL Bridge system overview", fontsize=19, color=INK, fontweight="bold", va="center")
    ax.text(0, 8.45, "Camera images are processed on the user's device", fontsize=13, color=MUTED, va="center")
    ax.text(0, 7.7, "Direction 1   Sign language to text and speech", fontsize=14.5, color=BL, fontweight="bold", va="center")
    steps = [("1", "User signs", "in front of a webcam\nor a phone camera"),
             ("2", "Hand points", "MediaPipe finds 21 points\nper hand: 126 values\nper frame"),
             ("3", "Cut the sign", "Starts when the hand moves,\nends when still; resampled\nto 30 frames"),
             ("4", "Classify word", "An LSTM predicts\nthe word from\nthe 30 frames"),
             ("5", "Answer or decline", "Above the threshold:\nshow the word\nBelow: say \"not sure\"")]
    bw, gap = 3.62, 0.48
    for i, (n, t, d) in enumerate(steps):
        x = i * (bw + gap)
        ax.add_patch(FancyBboxPatch((x, 5.45), bw, 1.5, boxstyle="round,pad=0,rounding_size=0.15", fc=BLF, ec=BL, lw=1.6))
        ax.add_patch(Circle((x + 0.42, 6.2), 0.3, fc=BL, ec="none"))
        ax.text(x + 0.42, 6.2, n, ha="center", va="center", fontsize=14, color="white", fontweight="bold")
        ax.text(x + 0.85, 6.2, t, ha="left", va="center", fontsize=10.6, color=INK, fontweight="bold")
        ax.text(x + bw / 2, 4.55, d, ha="center", va="center", fontsize=9.8, color=MUTED, linespacing=1.3)
        if i < 4:
            arr(ax, (x + bw + 0.04, 6.2), (x + bw + gap - 0.04, 6.2), col=BL)
    ax.text(0, 3.25, "Direction 2   Speech or text to sign language", fontsize=14.5, color="#2E7D5B", fontweight="bold", va="center")
    steps2 = [("1", "Speak or type", "A hearing user speaks or types Thai"),
              ("2", "Split into words", "Break the sentence into words"),
              ("3", "Look up the word list", "Match against the supported words"),
              ("4", "Show the sign", "Show the clip or dictionary link;\nsay so if the word is missing")]
    bw2, gap2 = 4.3, 0.75
    for i, (n, t, d) in enumerate(steps2):
        x = i * (bw2 + gap2)
        ax.add_patch(FancyBboxPatch((x, 1.45), bw2, 1.2, boxstyle="round,pad=0,rounding_size=0.15", fc="#E4F2EA", ec="#2E7D5B", lw=1.6))
        ax.add_patch(Circle((x + 0.42, 2.05), 0.28, fc="#2E7D5B", ec="none"))
        ax.text(x + 0.42, 2.05, n, ha="center", va="center", fontsize=13, color="white", fontweight="bold")
        ax.text(x + 0.85, 2.05, t, ha="left", va="center", fontsize=10.6, color=INK, fontweight="bold")
        ax.text(x + bw2 / 2, 0.8, d, ha="center", va="center", fontsize=9.8, color=MUTED, linespacing=1.3)
        if i < 3:
            arr(ax, (x + bw2 + 0.04, 2.05), (x + bw2 + gap2 - 0.04, 2.05), col="#2E7D5B")
    fig.savefig(os.path.join(out, "fig23_system_overview_en.png"), facecolor="white", bbox_inches="tight", pad_inches=0.1); plt.close(fig)

fig22(); fig22('en'); fig23(); fig23_en(); print("saved fig22, fig23 in", out)
