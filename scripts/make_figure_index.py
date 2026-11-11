# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Index of the final figures, grouped by overview step. Writes research/figures_v3/INDEX.html (self-contained, thumbnails embedded)
and INDEX.md. Superseded versions live in research/figures_v3/_superseded/.
  python3 scripts/make_figure_index.py
"""
import base64, io, os, sys
from PIL import Image
D = "research/figures_v3/"
# (file or None, caption) per language; None = not made yet
STEPS = [
 ("Overview", "#6B7280", "Your own Canva System Overview panel is the main one. fig24 is an alternative whose step 4 does not match your definition (it shows answer-or-not-sure, now part of step 3).", [
   ("Alternative 4-step overview (not your definition)", "fig24_overview4_th.png", "fig24_overview4_en.png"),
   ("Visual abstract", "fig10_graphical_abstract.png", None),
   ("Both directions of the system (spare)", "fig23_system_overview.png", "fig23_system_overview_en.png"),
   ("Research design chart, 5 groups (spare: repeats the left pipeline)", "fig12_research_design.png", "fig12_research_design_en.png")]),
 ("Step 1  ทำท่าภาษามือผ่านกล้อง (Sign in front of the camera)", "#E57A7A", "Tracker: trackers4/tracker4_1.png", [
   ("Recording workflow", "fig22_collection_workflow.png", "fig22_collection_workflow_en.png"),
   ("What the data looks like", "fig17_data_look.png", "fig17_data_look_en.png"),
   ("How the dataset is organised", "fig14a.png", "fig14a_en.png"),
   ("Signs per signer (S01 + S03 = 73%)", "fig14b.png", "fig14b_en.png"),
   ("7,267 videos to 6,688 signs", "fig11_data_funnel.png", "fig11_data_funnel_en.png")]),
 ("Step 2  อ่านมือด้วย MediaPipe (Read the hands with MediaPipe)", "#F0A34A", "Tracker: trackers4/tracker4_2.png", [
   ("How a sign is cut to 30 frames", "fig15_capture_timeline.png", "fig15_capture_timeline_en.png"),
   ("Left-right hand handling", "fig18_leftright_card.png", None),
   ("Hand position relative to the face", "fig19_face_relative_card.png", None)]),
 ("Step 3  LSTM เดาคำศัพท์ (LSTM guesses the word)", "#5DBB5D", "Tracker: trackers4/tracker4_3.png. Includes the confidence threshold (moved from the old step 4).", [
   ("Plain LSTM vs LSTM + DANN", "fig20_dann_card.png", "fig20_dann_card_en.png"),
   ("The DANN idea (backup: you are drawing your own)", "fig21_dann_idea.png", None),
   ("Confidence threshold per word", "fig25_threshold_th.png", "fig25_threshold_en.png"),
   ("Promised vs actual accuracy", "fig26_threshold_evidence_th.png", "fig26_threshold_evidence_en.png")]),
 ("Step 4  ประกอบประโยคและประมวลผล (Build the sentence and output)", "#5B7FE0", "Tracker: trackers4/tracker4_4.png. PROTOTYPE, not evaluated with volunteers (paper 3.5).", [
   ("Step 4 on the real demo: words + face become a sentence (prototype)", "fig27_demo.png", "fig27_demo_en.png")]),
 ("RESULT panel", "#B5483A", "New first-glance cards (r = result version), all with TH and EN.", [
   ("Random split vs unseen signer: 84.8 vs 51.9 (hero)", "fig6r_random_vs_unseen.png", "fig6r_random_vs_unseen_en.png"),
   ("5 rounds with results: plain LSTM vs DANN per signer", "fig16r_loso_result.png", "fig16r_loso_result_en.png"),
   ("Left-right handling: +16 points", "fig3r_handedness.png", "fig3r_handedness_en.png"),
   ("Per-word accuracy in three buckets", "fig2r_per_word.png", "fig2r_per_word_en.png"),
   ("Which words get confused (matrix + top mix-ups)", "fig13r_confusion.png", "fig13r_confusion_en.png"),
   ("Face-relative per word: 6 better, 3 worse", "fig4r_face_relative.png", "fig4r_face_relative_en.png"),
   ("The 5 rounds, method view (no results)", "fig16_loso_rounds.png", "fig16_loso_rounds_en.png")]),
 ("Older versions and spares", "#6B7280", "fig1, fig2, fig3, fig6 are kept in place because the report and slide builders read these file names", [
   ("OLD per signer, plain vs DANN (same data as fig16r)", "fig1_per_signer_plain_vs_dann.png", None),
   ("OLD per-word bars (replaced by fig2r)", "fig2_per_word_heldout.png", "../figures_v4_thai/fig2_per_word_heldout.png"),
   ("OLD left-right bars (replaced by fig3r)", "fig3_handedness.png", None),
   ("OLD random vs signer split (replaced by fig6r)", "fig6_random_vs_signer_split.png", None),
   ("OLD confusion matrix (replaced by fig13r)", "fig13_confusion_final28.png", None),
   ("OLD face-relative (replaced by fig4r)", "fig4_face_relative.png", "../figures_v4_thai/fig4_face_relative.png"),
   ("Data growth", "fig5_growth.png", None),
   ("Same word, different signers", "fig7_chan_tongkan_handshape.png", None),
   ("One hand vs two hands", "fig8_pawdhua_one_vs_two_hands.png", None)]),
]
def thumb(path, w=520):
    im = Image.open(D + path).convert("RGBA"); bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im); im = bg.convert("RGB")
    im.thumbnail((w, w)); b = io.BytesIO(); im.save(b, "JPEG", quality=82); return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
missing = []
html = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ThSL figures by step</title><style>',
 'body{font:15px/1.5 -apple-system,"Helvetica Neue",Arial,sans-serif;margin:0;background:#f6f7f9;color:#1f2937}main{max-width:1180px;margin:0 auto;padding:20px 16px 48px}',
 'h1{font-size:22px;margin:0 0 4px}.sub{color:#4b5563;margin:0 0 18px}',
 'h2{font-size:18px;margin:30px 0 2px;padding-left:10px;border-left:6px solid var(--c)}.note{color:#4b5563;margin:0 0 10px 16px;font-size:13px}',
 '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}.card{background:#fff;border:1px solid #e3e7ee;border-radius:8px;padding:10px}',
 '.t{font-weight:600;margin:0 0 6px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}.one{display:block}',
 'figure{margin:0}img{width:100%;height:auto;border:1px solid #eef0f3;border-radius:4px;background:#fff}figcaption{font-size:12px;color:#4b5563;margin-top:3px;word-break:break-all}',
 '.todo{display:flex;align-items:center;justify-content:center;min-height:90px;border:1px dashed #c7cdd6;border-radius:4px;color:#9aa3b2;font-size:12px;text-align:center}',
 '</style></head><body><main><h1>ThSL Bridge figures, by step</h1><p class="sub">Final set in research/figures_v3/. Superseded versions are in _superseded/. TH = Thai text, EN = English text.</p>']
md = ["# ThSL Bridge figures, by step", "", "Final set in `research/figures_v3/`. Superseded versions are in `_superseded/`. TH = Thai text, EN = English text.", ""]
for title, col, note, items in STEPS:
    html.append(f'<h2 style="--c:{col}">{title}</h2><p class="note">{note}</p><div class="grid">'); md += [f"## {title}", f"_{note}_", "", "| Figure | TH | EN |", "|---|---|---|"]
    for name, th, en in items:
        for f in (th, en):
            if f and not os.path.exists(D + f): missing.append(f)
        if th is None:
            html.append(f'<div class="card"><p class="t">{name}</p><div class="todo">to draw</div></div>'); md.append(f"| {name} | to draw | to draw |"); continue
        pair = en is not None
        html.append(f'<div class="card"><p class="t">{name}</p><div class="{"pair" if pair else "one"}">')
        html.append(f'<figure><img src="{thumb(th)}" alt="{name}"><figcaption>{"TH · " if pair else ""}{th}</figcaption></figure>')
        if pair: html.append(f'<figure><img src="{thumb(en)}" alt="{name} (English)"><figcaption>EN · {en.replace("../", "")}</figcaption></figure>')
        html.append("</div></div>")
        md.append(f"| {name} | `{th}` | " + (f"`{en}`" if en else "to do") + " |")
    html.append("</div>"); md.append("")
html.append("</main></body></html>")
if missing: sys.exit("MISSING: " + ", ".join(missing))
open(D + "INDEX.html", "w", encoding="utf-8").write("\n".join(html)); open(D + "INDEX.md", "w", encoding="utf-8").write("\n".join(md))
print("ok", os.path.getsize(D + "INDEX.html") // 1024, "KB;", sum(len(i[3]) for i in STEPS), "figure entries")
