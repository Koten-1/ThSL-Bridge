# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Confusion matrices (face-relative model vs picture-coordinate model, 13 symptom words, leave-one-signer-out) and a live test sheet.

  python3 scripts/make_test_sheet.py OUT.md
Reads research/loso_setA_head/oof_base.csv (face-relative) and research/loso_setA/oof_base.csv (picture coordinates, same data and settings).
Predictions are the average of 3 seeds for clips of the signer who was held out.
"""
import csv, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = {"head": ROOT / "research/loso_setA_head/oof_base.csv", "raw": ROOT / "research/loso_setA/oof_base.csv"}
WORDS = ["ปวดท้อง", "ปวดหัว", "ไข้", "ไอ", "เวียนหัว", "อาเจียน", "ท้องเสีย", "แพ้ยา", "เจ็บคอ", "แพ้อาหาร", "น้ำมูกไหล", "หายใจ", "เจ็บ"]


def load(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def acc(rows, word=None, signers=None):
    rs = [r for r in rows if (word is None or r["true"] == word) and (signers is None or r["signer"] in signers)]
    return (100 * sum(r["true"] == r["pred"] for r in rs) / len(rs), len(rs)) if rs else (float("nan"), 0)


def matrix(rows, signers):
    c = Counter((r["true"], r["pred"]) for r in rows if r["signer"] in signers)
    return c


def main():
    rows = {k: load(v) for k, v in RUNS.items()}
    names = {"head": "สัมพัทธ์กับใบหน้า (โมเดลทดลอง)", "raw": "พิกัดในภาพ (ปกติ)"}
    L = ["# ใบทดสอบ: โมเดลอาการ 13 คำ แบบสัมพัทธ์กับใบหน้า เทียบกับแบบพิกัดในภาพ\n",
         "ตัวเลขทั้งหมดมาจากการกันผู้แสดงออกทีละคน (ผู้แสดง S01 ถึง S04 ที่โมเดลไม่เคยเห็นตอนฝึก) เฉลี่ย 3 ค่าเริ่มต้นสุ่ม ใช้ข้อมูลและการตั้งค่าชุดเดียวกัน ต่างกันที่วิธีเขียนพิกัดมือเท่านั้น "
         "S04 นั่งใกล้กล้องมากและถ่ายแนวตั้ง จึงแยกรายงาน ผู้แสดงที่ไม่ใช่ S04 คือ S01 S02 S03 ซึ่งถ่ายแนวนอนไกลกว่า\n",
         "## 1. ความแม่นยำรายคำ (%)\n",
         "| # | คำ | พิกัดในภาพ S01–S03 | สัมพัทธ์ใบหน้า S01–S03 | ผลต่าง | พิกัดในภาพ S04 | สัมพัทธ์ใบหน้า S04 |", "|---|---|---|---|---|---|---|"]
    main3 = {"S01", "S02", "S03"}
    for i, w in enumerate(WORDS, 1):
        r3, h3 = acc(rows["raw"], w, main3)[0], acc(rows["head"], w, main3)[0]
        r4, n4 = acc(rows["raw"], w, {"S04"}); h4 = acc(rows["head"], w, {"S04"})[0]
        s4 = lambda v: "ไม่มีข้อมูล" if n4 == 0 else f"{v:.0f}"
        L.append(f"| {i} | {w} | {r3:.0f} | {h3:.0f} | {h3 - r3:+.0f} | {s4(r4)} | {s4(h4)} |")
    ra, ha = acc(rows["raw"], None, main3)[0], acc(rows["head"], None, main3)[0]
    L.append(f"| | **รวมทุกคลิป** | **{ra:.1f}** | **{ha:.1f}** | **{ha - ra:+.1f}** | **{acc(rows['raw'], None, {'S04'})[0]:.1f}** | **{acc(rows['head'], None, {'S04'})[0]:.1f}** |")
    L.append("\nตัวเลขรวมนี้นับตามจำนวนคลิป จึงต่างจาก 72.7% และ 78.6% ในรายงาน ซึ่งเป็นค่าเฉลี่ยรายผู้แสดง\n")

    for key in ("head", "raw"):
        L.append(f"## 2.{'1' if key == 'head' else '2'} ตารางความสับสน: {names[key]} (ผู้แสดง S01–S03)\n")
        L.append("แถว = คำที่ทำจริง คอลัมน์ = คำที่โมเดลทาย ตัวเลขคือจำนวนคลิป (ตัวเลขที่ทายผิดเน้นตัวหนา)\n")
        c = matrix(rows[key], main3)
        L.append("| คำที่ทำจริง | " + " | ".join(str(i) for i in range(1, 14)) + " | อื่น ๆ |")
        L.append("|" + "-" * 15 + "|" + ("-" * 7 + "|") * 13 + "-" * 7 + "|")
        for i, w in enumerate(WORDS, 1):
            cells = []; tot = sum(v for (t, p), v in c.items() if t == w)
            for j, p in enumerate(WORDS, 1):
                v = c[(w, p)]
                cells.append("" if v == 0 else (f"{v}" if i == j else f"**{v}**"))
            other = sum(v for (t, p), v in c.items() if t == w and p not in WORDS)
            L.append(f"| {i} {w} | " + " | ".join(cells) + f" | {other if other else ''} |")
        L.append("")
    L.append("ตัวเลขหัวคอลัมน์: " + " ".join(f"{i}={w}" for i, w in enumerate(WORDS, 1)) + "\n")

    L.append("## 3. คำที่ผิดบ่อยที่สุด (S01–S03 รวมกัน)\n")
    for key in ("head", "raw"):
        c = matrix(rows[key], main3)
        top = [(t, p, v) for (t, p), v in c.most_common() if t != p][:8]
        L.append(f"- {names[key]}: " + "; ".join(f"{t}→{p} {v}" for t, p, v in top))
    L.append("\n**S04 (นั่งใกล้กล้อง)**\n")
    for key in ("head", "raw"):
        c = matrix(rows[key], {"S04"})
        top = [(t, p, v) for (t, p), v in c.most_common() if t != p][:6]
        L.append(f"- {names[key]}: " + "; ".join(f"{t}→{p} {v}" for t, p, v in top))
    L.append("")

    L.append("## 4. สิ่งที่ต้องทดสอบสด\n")
    L.append("**เตรียม** เปิด http://localhost:8000/ ติ๊ก \"ใช้เฉพาะผู้ใช้หลัก\" (โมเดลสัมพัทธ์ต้องเห็นใบหน้า) เปิดสวิตช์ตรวจสอบ (diagnostics) เลือกโมเดลสลับกันระหว่าง **อาการ 13 คำ · สัมพัทธ์ใบหน้า (ทดลอง)** กับ **โมเดลใหม่ (28 คำ)** ดูตัวเลข \"ใบหน้ากว้าง ...%\" ข้างปุ่มโมเดลเพื่อบันทึกระยะ\n")
    L.append("**ทำเงื่อนไข 3 แบบ** ทำแต่ละท่า 10 ครั้งต่อเงื่อนไขต่อโมเดล: (ก) นั่งใกล้ ใบหน้ากว้างราว 10 ถึง 14% (ข) นั่งใกล้กว่า ใบหน้ากว้างราว 20 ถึง 25% (ค) นั่งไกลกว่าปกติ ใบหน้ากว้างต่ำกว่า 8%\n")
    L.append("**คำที่ควรทดสอบก่อน** (เรียงตามเหตุผล)\n")
    L.append("| คำ | ทำไมต้องทดสอบ | ผลคาดจากข้อมูล (สัมพัทธ์ / ปกติ, S01–S03) |\n|---|---|---|")
    why = {"อาเจียน": "พิกัดสัมพัทธ์แก้ S03 ได้ ทดสอบว่าสดก็ดีขึ้นไหม",
           "ปวดหัว": "ที่คุณเจอผิดสด ข้อมูลบอกว่าพังเฉพาะ S04 (นั่งใกล้กล้อง) ทดสอบที่ระยะใกล้โดยเฉพาะ",
           "เวียนหัว": "พิกัดสัมพัทธ์ทำให้ลดจาก 100% เหลือ 60% ในข้อมูลบางส่วน ทดสอบว่าสดแย่ลงไหม",
           "ไข้": "ลดจาก 99% เหลือ 77% ในข้อมูลบางส่วน",
           "ปวดท้อง": "ลดจาก 96% เหลือ 75% ในข้อมูลบางส่วน และเป็นคำที่ท้องอยู่ต่ำสุดของภาพ",
           "หายใจ": "ดีขึ้นมากจาก 33% เป็น 100% ในข้อมูล ทดสอบว่าจริงไหม",
           "น้ำมูกไหล": "ดีขึ้นจาก 73% เป็น 100% ในข้อมูล"}
    for w in ["อาเจียน", "ปวดหัว", "เวียนหัว", "ไข้", "ปวดท้อง", "หายใจ", "น้ำมูกไหล"]:
        r3, h3 = acc(rows["raw"], w, main3)[0], acc(rows["head"], w, main3)[0]
        L.append(f"| {w} | {why[w]} | {h3:.0f}% / {r3:.0f}% |")
    L.append("\n**ตารางบันทึก (กรอกเอง)** จำนวนครั้งที่ถูกจาก 10 ครั้ง\n")
    L.append("| คำ | ใกล้ ปกติ | ใกล้ สัมพัทธ์ | ใกล้กว่า ปกติ | ใกล้กว่า สัมพัทธ์ | ไกล ปกติ | ไกล สัมพัทธ์ | ทายเป็นคำอะไรบ่อยสุด |\n|---|---|---|---|---|---|---|---|")
    for w in ["อาเจียน", "ปวดหัว", "เวียนหัว", "ไข้", "ปวดท้อง", "หายใจ", "น้ำมูกไหล"]:
        L.append(f"| {w} | | | | | | | |")
    L.append("\n**ตัดสินอย่างไร:** โมเดลสัมพัทธ์ถือว่าดีกว่าสำหรับการใช้งานของคุณ ถ้าถูกรวมทั้งตารางมากกว่าโมเดลปกติอย่างน้อย 10 ครั้งจาก 210 ครั้ง (7 คำ × 3 เงื่อนไข × 10 ครั้ง) และไม่ลดลงในคำใดคำหนึ่งเกิน 4 ครั้งจาก 30 ถ้าไม่ได้ตามนี้ ให้ใช้โมเดลปกติต่อ\n")
    L.append("**เก็บหลักฐาน** กดดาวน์โหลดท่าที่จับได้ (ปุ่มใต้สวิตช์ตรวจสอบ) หลังจบแต่ละเงื่อนไข ไฟล์มีค่าจุดข้อต่อ คำที่ตั้งใจ คำที่โมเดลทาย และความกว้างใบหน้า ส่งให้ผมวิเคราะห์ต่อได้\n")
    L.append("**ข้อจำกัดที่ต้องรู้:** โมเดลสัมพัทธ์ฝึกกับ 13 คำอาการเท่านั้น (ไม่มี ขอบคุณ ไม่ ช่วย ฯลฯ) และยังไม่เคยทดสอบสดกับกล้องจริง ผลในตารางด้านบนมาจากผู้แสดง S01–S04 ที่ถ่ายด้วยสมาร์ตโฟนในห้องบันทึก ตัวเลขใบหน้ากว้างในแอปวัดจากตัวตรวจใบหน้าตัวเดียวกับตอนทำข้อมูลฝึก แต่ในแอปวัดทุกครึ่งวินาที ไม่ใช่จากภาพแรกของคลิป")
    Path(sys.argv[1]).write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
