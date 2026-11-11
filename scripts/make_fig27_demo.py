# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""fig27: step 4 shown on the REAL demo UI (screenshots in research/figures_v3/ui_shots/, taken headless with NO camera and
example input fed to the app's own functions: scripts/capture_demo_shots.py). Highlight boxes + numbered callouts.
  python3 scripts/make_fig27_demo.py research/figures_v3
"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle, FancyBboxPatch

B, BD, INK, MUTED = "#5B7FE0", "#3A5BC7", "#1F2937", "#4B5563"
out = sys.argv[1]; U = os.path.join(out, "ui_shots")
side = mpimg.imread(os.path.join(U, "demo_sentence_cards.png"))[:1290]
sett = mpimg.imread(os.path.join(U, "demo_face_settings.png"))
TXT = {
 "th": dict(font="TH Sarabun New", fs=1.0, title="จากเดโมจริง: คำ + สีหน้า เป็นประโยค", badge="ต้นแบบ ยังไม่ได้ประเมินกับผู้ใช้",
   c=["ป้ายสีหน้าบนคำ:\nถาม หรือ ปฏิเสธ", "ประโยควาง “ไม่”\nไว้หน้าคำที่ถูกปฏิเสธ", "คำที่มีป้าย “ถาม”\nทำให้ประโยคลงท้าย\nด้วย “ไหม?”",
      "คิ้วยกหรือขมวดเกินหน้านิ่งของผู้ใช้ = ถาม", "ส่ายหน้าซ้ายขวาเกินองศาที่ตั้งไว้ = ปฏิเสธ"],
   foot="ภาพหน้าจอเดโมพร้อมตัวอย่างข้อมูล (ไม่ได้เปิดกล้อง ไม่มีใบหน้าในภาพ) ป้ายสีหน้าเป็นกฎที่ยังรอยืนยันกับผู้ใช้ภาษามือ ไม่ใช่ผลจากโมเดลที่ฝึกแล้ว"),
 "en": dict(font=["Helvetica", "TH Sarabun New"], fs=0.8, title="From the real demo: words + face become a sentence", badge="Prototype: not yet evaluated with users",
   c=["Face tag on the word:\nquestion or negation", "“ไม่” is placed before\nthe negated word", "A word tagged “question”\nends the sentence\nwith “ไหม?”",
      "Eyebrows raised or furrowed past the user's neutral face = question", "Head turned left–right past a set angle = negation"],
   foot="Demo screenshots with example input (no camera, no face in the picture). Face tags are rules still awaiting confirmation with sign language users, not a trained model."),
}
def make(lang):
    T = TXT[lang]; plt.rcParams["font.family"] = T["font"]; k = T["fs"]
    fig = plt.figure(figsize=(15, 8.6), dpi=200, facecolor="white")
    fig.text(0.02, 0.955, T["title"], fontsize=24 * k, color=INK, fontweight="bold", va="center")
    bw = 0.30 if lang == "en" else 0.25
    fig.patches.append(FancyBboxPatch((0.98 - bw, 0.92), bw, 0.07, boxstyle="round,pad=0,rounding_size=0.01", fc="#FFF4D6", ec="#C9A400", lw=2, transform=fig.transFigure, figure=fig))
    fig.text(0.98 - bw / 2, 0.955, T["badge"], ha="center", va="center", fontsize=16 * k, color="#7A5B00", fontweight="bold")
    a1 = fig.add_axes([0.02, 0.09, 0.327, 0.80]); a1.imshow(side); a1.axis("off")
    a2 = fig.add_axes([0.54, 0.43, 0.44, 0.44]); a2.imshow(sett); a2.axis("off")
    def hl(ax, x0, y0, x1, y1, n, bx, by):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=B, lw=4, zorder=5))
        ax.text(bx, by, str(n), ha="center", va="center", fontsize=15, color="white", fontweight="bold", zorder=6,
                bbox=dict(boxstyle="circle,pad=0.35", fc=BD, ec="white", lw=1.5))
    hl(a1, 284, 104, 618, 200, 1, 618, 88); hl(a1, 38, 218, 505, 282, 2, 530, 250); hl(a1, 44, 700, 452, 1140, 3, 480, 722)
    hl(a2, 28, 212, 1408, 418, 4, 1370, 238); hl(a2, 28, 452, 1408, 545, 5, 1370, 474)
    # legend (middle column and under the settings picture), aligned to the highlights
    def ytop(py): return 0.09 + 0.80 * (1 - py / 1290)
    for n, py, x in ((1, 150, 0.375), (2, 250, 0.375), (3, 920, 0.375)):
        fig.text(x, ytop(py), f"{n}", ha="center", va="center", fontsize=15, color="white", fontweight="bold", bbox=dict(boxstyle="circle,pad=0.35", fc=BD, ec="white"))
        fig.text(x + 0.014, ytop(py), T["c"][n - 1], ha="left", va="center", fontsize=15 * k if lang == "th" else 12.5, color=INK, linespacing=1.25)
    for n, y in ((4, 0.34), (5, 0.26)):
        fig.text(0.545, y, f"{n}", ha="center", va="center", fontsize=15, color="white", fontweight="bold", bbox=dict(boxstyle="circle,pad=0.35", fc=BD, ec="white"))
        fig.text(0.56, y, T["c"][n - 1], ha="left", va="center", fontsize=16 * k if lang == "th" else 13, color=INK)
    fig.text(0.02, 0.03, T["foot"], fontsize=12.5 * k if lang == "th" else 10.5, color=MUTED, va="center")
    fig.savefig(os.path.join(out, "fig27_demo" + ("_en" if lang == "en" else "") + ".png"), facecolor="white"); plt.close(fig)
for lg in ("th", "en"): make(lg)
print("saved fig27_demo th+en")
