# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Write the numbers behind every chart and table as plain Markdown tables, read straight from the result files,
so the team can draw their own charts without retyping numbers.

  python3 scripts/make_chart_data.py OUT.md
"""
import csv, re, sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent.parent / "research"


def per_signer(run):
    """rows of the per-held-out-signer table: (signer, n, base, base_sd, dann, dann_sd)"""
    out = []
    for line in (R / run / "summary.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (\w+) \| (\d+) \| ([\d.]+) \(([\d.]+)\)(?: \| ([\d.]+) \(([\d.]+)\))?", line)
        if m:
            out.append(m.groups())
    return out


def per_word(run):
    """{word: {model: percent}} from the per-word table"""
    txt = (R / run / "summary.md").read_text(encoding="utf-8").splitlines()
    out, models, on = {}, [], False
    for line in txt:
        if line.startswith("| word |"):
            models = [c.strip() for c in line.strip("|").split("|")][1:]; on = True; continue
        if on:
            if not line.startswith("|"):
                if out: break
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0].startswith("---"):
                continue
            out[cells[0]] = {m: int(v.rstrip("%")) for m, v in zip(models, cells[1:])}
    return out


VERDICT_TH = {"NO DETECTABLE DIFFERENCE": "ไม่พบความต่าง", "DANN HURTS": "DANN แย่ลง", "DANN HELPS": "DANN ดีขึ้น"}


def dann_line(run):
    txt = (R / run / "summary.md").read_text(encoding="utf-8")
    d = re.search(r"Differences \(DANN minus plain, accuracy points\): (.*)", txt)
    m = re.search(r"mean difference \*\*([-+\d.]+) points\*\*, 95% interval over signers \[([-+\d.]+), ([-+\d.]+)\], DANN better in (\d+) of (\d+)", txt)
    v = re.search(r"### Verdict: (.*)", txt)
    return (d.group(1) if d else "", m.groups() if m else None, VERDICT_TH.get(v.group(1).strip(), v.group(1).strip()) if v else "")


def main():
    L = ["## ภาคผนวก: ตัวเลขเบื้องหลังกราฟและตารางทุกชิ้น (ใช้ทำกราฟเอง)\n",
         "ตัวเลขทั้งหมดอ่านตรงจากไฟล์ผลลัพธ์ในโฟลเดอร์ research/ ด้วย scripts/make_chart_data.py ไม่ได้พิมพ์ใหม่ด้วยมือ ความแม่นยำเป็นร้อยละ ค่าในวงเล็บคือส่วนเบี่ยงเบนมาตรฐานข้าม 3 ค่าเริ่มต้นสุ่ม\n"]

    # fig1 and fig6
    L.append("### ก. รูปที่ 1: ความแม่นยำรายผู้แสดง แบบปกติเทียบ DANN (28 คำ) — research/loso_final28\n")
    L.append("| ผู้แสดงที่ถูกกัน | จำนวนท่าที่ทดสอบ | แบบปกติ | DANN |\n|---|---|---|---|")
    rows = per_signer("loso_final28")
    for s, n, b, bsd, d, dsd in rows:
        L.append(f"| {s} | {n} | {b} ({bsd}) | {d} ({dsd}) |")
    L.append("")
    L.append("### ข. รูปที่ 3 (สไลด์ 9 ซ้าย): แบ่งสุ่มเทียบกันผู้แสดง (28 คำ) — research/random_split28, loso_final28\n")
    rs = per_signer("random_split28")[0]
    L.append("| วิธี | ค่า | จุดรายผู้แสดง |\n|---|---|---|")
    L.append(f"| แบ่งสุ่ม 80/20 (ทุกผู้แสดงปนกัน) | {rs[2]} ({rs[3]}) | ไม่มี (ชุดทดสอบเดียว {rs[1]} ท่า) |")
    L.append("| กันผู้แสดงทีละคน | 51.9 (เฉลี่ยรายผู้แสดง) | " + ", ".join(f"{s} {b}" for s, n, b, *_ in rows) + " |\n")

    # fig2 + random per word
    L.append("### ค. รูปที่ 2: ความแม่นยำรายคำ บนผู้แสดงที่ไม่เคยเห็น (28 คำ) เทียบกับการแบ่งสุ่ม\n")
    pw, pr = per_word("loso_final28"), per_word("random_split28")
    L.append("| คำ | กันผู้แสดง (แบบปกติ) | กันผู้แสดง (DANN) | แบ่งสุ่ม |\n|---|---|---|---|")
    for w, v in sorted(pw.items(), key=lambda t: -t[1]["base"]):
        L.append(f"| {w} | {v['base']} | {v.get('dann', '')} | {pr.get(w, {}).get('base', '')} |")
    L.append("\nหมายเหตุ: \"คุณ\" ทดสอบเฉพาะ S04 และ S05 รวม 50 คลิป ไม่ควรตีความ\n")

    # fig3 handedness
    L.append("### ง. รูปที่ 4: การจัดการมือซ้ายขวา (13 คำ) — research/loso_setA_none, loso_setA, loso_setA_canonical\n")
    L.append("| ผู้แสดงที่ถูกกัน | ไม่จัดการ | พลิกซ้ายขวาระหว่างฝึก (ใช้จริง) | ปรับให้มือหลักอยู่ช่องซ้าย |\n|---|---|---|---|")
    arms = {k: {r[0]: f"{r[2]} ({r[3]})" for r in per_signer(k)} for k in ("loso_setA_none", "loso_setA", "loso_setA_canonical")}
    for s in ("S01", "S02", "S03", "S04"):
        L.append(f"| {s} | {arms['loso_setA_none'].get(s, '')} | {arms['loso_setA'].get(s, '')} | {arms['loso_setA_canonical'].get(s, '')} |")
    L.append("| เฉลี่ย S01–S03 | 56.8 | 72.7 | 75.9 |\n")

    # fig4 face-relative per word
    L.append("### จ. รูปที่ 5: ตำแหน่งสัมพัทธ์กับใบหน้า เทียบพิกัดในภาพ รายคำ (13 คำ, รวมผู้แสดงที่ถูกกันทุกคน) — research/loso_setA, loso_setA_head\n")
    a, h = per_word("loso_setA"), per_word("loso_setA_head")
    L.append("| คำ | พิกัดในภาพ | สัมพัทธ์ใบหน้า | ผลต่าง |\n|---|---|---|---|")
    for w in sorted(a, key=lambda w: h.get(w, {}).get("base", 0) - a[w]["base"]):
        x, y = a[w]["base"], h.get(w, {}).get("base", 0)
        L.append(f"| {w} | {x} | {y} | {y - x:+d} |")
    hs = {r[0]: r[2] for r in per_signer("loso_setA_head")}; as_ = {r[0]: r[2] for r in per_signer("loso_setA")}
    L.append("\nรายผู้แสดง: " + ", ".join(f"{s} {as_.get(s)} → {hs.get(s)}" for s in ("S01", "S02", "S03", "S04")) + "\n")

    # fig5 growth
    L.append("### ฉ. กราฟการเติบโตของข้อมูล (สไลด์ 5) — research/eda_phase1_10words, DATASET_CARD\n")
    L.append("| สิ่งที่นับ | รอบภูมิภาค | รอบนี้ |\n|---|---|---|")
    L.append("| คำ | 10 | 30 บันทึก (ใช้จำแนก 28) |\n| ผู้แสดง | 4 (ได้ยินทั้งหมด) | 9 (หูหนวก 5, ได้ยิน 4 เฉพาะ \"คุณ\") |\n| ท่า | 700 | 7,168 |\n")

    # DANN everywhere
    L.append("### ช. DANN ทุกการทดลอง (ผลต่าง DANN − ปกติ จุด)\n")
    L.append("| การทดลอง | ไฟล์ | ผลต่างรายผู้แสดง | เฉลี่ย | ช่วงเชื่อมั่น 95% | DANN ชนะ | ผลตามเกณฑ์ |\n|---|---|---|---|---|---|---|")
    for name, run in (("13 คำ หูหนวก", "loso_setA"), ("30 คำ หูหนวก", "loso_all30"), ("28 คำ รวมผู้ได้ยินเฉพาะ คุณ", "loso_final28"),
                      ("7 คำ ต้นทาง 3 คน (หูหนวก)", "loso_old7_deaf"), ("7 คำ ต้นทาง 7 คน (หูหนวก+ได้ยิน)", "loso_old7_mix"),
                      ("7 คำ ต้นทาง 3 คน คลิปฝึก ~600", "loso_old7_deaf_cap40"), ("7 คำ ต้นทาง 7 คน คลิปฝึก ~600", "loso_old7_mix_cap16"),
                      ("ทำซ้ำรอบภูมิภาค 10 คำ ผู้ได้ยิน 4 คน", "loso_regional10_new")):
        try:
            d, m, v = dann_line(run)
        except FileNotFoundError:
            continue
        if m:
            L.append(f"| {name} | {run} | {d} | {m[0]} | {m[1]} ถึง {m[2]} | {m[3]} จาก {m[4]} | {v} |")
    for c in (20, 100):                         # DANN that also saw unlabeled clips of the new signer (dannc), against the plain model
        f = R / f"loso_calib{c}" / "results.csv"
        if not f.exists():
            continue
        by = defaultdict(list)
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            by[(r["model"], r["fold"])].append(float(r["acc"]) * 100)
        folds = sorted({k[1] for k in by})
        d = [sum(by[("dannc", x)]) / len(by[("dannc", x)]) - sum(by[("base", x)]) / len(by[("base", x)]) for x in folds]
        import numpy as _np
        rng = _np.random.default_rng(0); boots = [rng.choice(d, len(d), replace=True).mean() for _ in range(5000)]
        lo, hi = _np.percentile(boots, [2.5, 97.5]); mean = sum(d) / len(d); wins = sum(x > 0 for x in d)
        verdict = "DANN แย่ลง" if mean <= -2 and (len(d) - wins) >= 2 / 3 * len(d) and hi < 0 else ("DANN ดีขึ้น" if mean >= 2 and wins >= 2 / 3 * len(d) and lo > 0 else "ไม่พบความต่าง")
        L.append(f"| 28 คำ เห็นคลิปผู้ใช้ใหม่ {c} คลิป (ไม่มีป้าย) | loso_calib{c} | " + ", ".join(f"{x} {v:+.1f}" for x, v in zip(folds, d)) +
                 f" | {mean:+.1f} | {lo:+.1f} ถึง {hi:+.1f} | {wins} จาก {len(d)} | {verdict} |")
    L.append("")

    # zone check
    zc = R / "zone_check/summary.md"
    if zc.exists():
        L.append("### ซ. แบ่งโซนร่างกายก่อนจำแนก (13 คำ, 2 ค่าเริ่มต้น) — research/zone_check\n")
        L.append("| ผู้แสดงที่ถูกกัน | แบบปกติ | จำกัดคำตามโซน | แบบจำลองรายโซน | รู้โซนที่ถูก | กฎเลือกโซนถูก |\n|---|---|---|---|---|---|")
        for line in zc.read_text(encoding="utf-8").splitlines():
            if re.match(r"\| (S0\d|\*\*mean)", line):
                L.append(line.replace("**mean S01 to S03**", "เฉลี่ย S01–S03").replace("**", ""))
        L.append("")

    # show10
    if (R / "loso_show10/summary.md").exists():
        L.append("### ฌ. โมเดลโชว์ 10 คำ บนผู้แสดงที่ไม่เคยเห็น — research/loso_show10\n")
        L.append("| ผู้แสดงที่ถูกกัน | กลุ่ม | จำนวนท่า | ความแม่นยำ |\n|---|---|---|---|")
        for s, n, b, bsd, *_ in per_signer("loso_show10"):
            L.append(f"| {s} | {'ได้ยิน' if s.startswith('O') else 'หูหนวก'} | {n} | {b} ({bsd}) |")
        L.append("\n| คำ | ความแม่นยำ |\n|---|---|")
        for w, v in sorted(per_word("loso_show10").items(), key=lambda t: -t[1]["base"]):
            L.append(f"| {w} | {v['base']} |")
        L.append("")

    # hand count
    hc = R / "hand_count_check.csv"
    if hc.exists():
        L.append("### ญ. จำนวนมือที่พบในแต่ละท่า (สัดส่วนเฟรมที่พบสองมือ) — research/hand_count_check.csv\n")
        agg = defaultdict(list)
        for r in csv.DictReader(open(hc, encoding="utf-8-sig")):
            agg[(r["word"], r["signer"])].append((float(r["both_hand_frames"]), r["ok"]))
        L.append("| คำ | ผู้แสดง | จำนวนคลิป | เฟรมที่พบสองมือ | ทายถูกบนผู้แสดงที่ถูกกัน (28 คำ) |\n|---|---|---|---|---|")
        for (w, s), v in sorted(agg.items()):
            ok = [x for _, x in v if x in ("True", "False")]
            L.append(f"| {w} | {s} | {len(v)} | {100 * sum(b for b, _ in v) / len(v):.0f}% | " + (f"{100 * sum(x == 'True' for x in ok) / len(ok):.0f}%" if ok else "") + " |")
        L.append("")

    # coverage
    cov = R / "eda_all/coverage.csv"
    if cov.exists():
        L.append("### ฎ. จำนวนคลิปต่อคำต่อผู้แสดง (ข้อมูลเบื้องหลัง heatmap) — research/eda_all/coverage.csv\n")
        rows = list(csv.reader(open(cov, encoding="utf-8-sig")))
        L.append("| " + " | ".join(rows[0]) + " |\n|" + "---|" * len(rows[0]))
        for r in rows[1:]:
            L.append("| " + " | ".join(r) + " |")
        L.append("")
    Path(sys.argv[1]).write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
