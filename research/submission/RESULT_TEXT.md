# RESULT panel text: the paper's research questions, answered

Source: `report_th.md` section 1.2 (questions), 4.3–4.8 (answers). Every number is from the paper or `research/loso_final28/summary.md`.

## The main question (paper 1.2)

TH: เมื่อผู้ใช้ใหม่ที่ระบบไม่เคยเห็นมาใช้ ความแม่นยำที่เสียไปมาจากปัจจัยใด เทคนิคใดช่วยได้ และระบบบอกได้หรือไม่ว่าคำตอบใดเชื่อได้

EN: When a new user the system has never seen arrives, where does the lost accuracy come from, which techniques help, and can the system tell which answers to trust?

## The six sub-questions and their answers

| Q | Question | Answer | Figure |
|---|---|---|---|
| 1 | How much does a random split overstate accuracy? | 33 points: 84.8% (random split) vs 51.9% (unseen signer) | `fig6r_random_vs_unseen` |
| 2 | Does DANN help on unseen signers? | No. 46.3% vs 51.9% (−5.6, interval −8.1 to −3.0), worse for all 5 signers | `fig16r_loso_result` |
| 3 | What does handling left and right hands do? | A lot: 56.8% → 72.7% (flip in training), 75.9% (main hand to slot 1), 13 words | `fig3r_handedness` |
| 4 | Does hand position relative to the face help? | Mixed: mean +5.9 on 13 words (72.7 → 78.6), 6 words better, 3 worse; not adopted | `fig4r_face_relative` |
| 5 | Can the confidence threshold be trusted on a new signer? | Not when set from a random split: promised 95.4%, got 66.2%. Set from other signers: 76.7% (answers 47% of signs). Averaging 3 models lifts accuracy 51.9 → 57.9 | `fig26_threshold_evidence` (step 3 card) |
| 6 | Can pre-training pose differences flag which (word, signer) pairs will fail? | Not confirmed. Exploratory: flagged pairs fail 55% vs 26% (p = 0.009), but this comes mainly from S04 and S05; without them 31% vs 27% | not drawn (QR page) |

Word-level support for the main question ("where does it fail?"): `fig2r_per_word` (11 words above 75%, 8 below 50%) and `fig13r_confusion` (most common mix-ups: cough → runny nose 55%, medicine → drug allergy 41%, eye → runny nose 41%, wait → drug allergy 41%, I ↔ want 37% / 36%).

## Overview text for the top of the RESULT panel (Thai)

```text
คำถามหลัก: เมื่อผู้ใช้ใหม่ที่ระบบไม่เคยเห็นมาใช้ ความแม่นยำที่เสียไปมาจากปัจจัยใด เทคนิคใดช่วยได้ และระบบบอกได้หรือไม่ว่าคำตอบใดเชื่อได้
☐ ข้อ 1 การแบ่งสุ่มสูงเกินจริงเท่าใด: 33 จุด (84.8% เทียบ 51.9% บนผู้แสดงที่ไม่เคยเห็น)
☐ ข้อ 2 DANN ช่วยหรือไม่: ไม่ช่วย 46.3% เทียบ 51.9% (−5.6) ต่ำกว่าในผู้แสดงทั้ง 5 คน
☐ ข้อ 3 จัดการมือซ้าย–ขวา: ช่วยมาก 56.8% เป็น 72.7% (+16 จุด)
☐ ข้อ 4 ตำแหน่งมือเทียบใบหน้า: บางคำดีขึ้น บางคำแย่ลง (เฉลี่ย +5.9 บน 13 คำ) ยังไม่นำมาใช้
☐ ข้อ 5 เชื่อค่าความเชื่อมั่นได้หรือไม่: เกณฑ์จากการสุ่มสัญญา 95.4% แต่ได้จริง 66.2% ตั้งจากผู้แสดงอื่นได้ 76.7% (ตอบ 47% ของท่า)
☐ ข้อ 6 บอกล่วงหน้าได้หรือไม่ว่าท่าใดจะพลาด: ยังไม่ยืนยัน (ผลเบื้องต้นมาจาก S04 และ S05 เป็นหลัก)
```

## Overview text (English)

```text
Main question: when a new user the system has never seen arrives, where does the lost accuracy come from, which techniques help, and can the system tell which answers to trust?
☐ Q1 How much does a random split overstate accuracy? 33 points (84.8% vs 51.9% on unseen signers)
☐ Q2 Does DANN help? No: 46.3% vs 51.9% (−5.6), lower for all 5 signers
☐ Q3 Left and right hand handling: a lot, 56.8% to 72.7% (+16 points)
☐ Q4 Hand position relative to the face: some words better, some worse (mean +5.9 on 13 words); not adopted
☐ Q5 Can the confidence be trusted? A threshold set from a random split promised 95.4% but delivered 66.2%; set from other signers: 76.7% (answers 47% of signs)
☐ Q6 Can we tell in advance which signs will fail? Not confirmed (the early result comes mainly from S04 and S05)
```

## Card titles and captions (finding as the title)

| Card | Thai title | English title | Caption (TH) |
|---|---|---|---|
| fig6r | การแบ่งแบบสุ่มทำให้ผลดูดีเกินจริง 33 จุด | A random split overstates accuracy by 33 points | ผู้ใช้ใหม่ได้ 51.9% ไม่ใช่ 84.8% |
| fig16r | ผลเมื่อทดสอบกับผู้แสดงที่โมเดลไม่เคยเห็น | Result on a signer the model has never seen | DANN ต่ำกว่าในผู้แสดงทั้ง 5 คน |
| fig3r | จัดการมือซ้าย–ขวา เพิ่มความแม่นยำราว 16 จุด | Handling left and right hands adds about 16 points | S02 จาก 35% เป็น 74% |
| fig4r | วัดตำแหน่งมือจากใบหน้า: 6 คำดีขึ้น 3 คำแย่ลง | Measuring the hand from the face: 6 words better, 3 worse | ผลต่างกันตามคำ จึงยังไม่นำมาใช้ |
| fig2r | 28 คำ: 11 คำแม่นเกิน 75% แต่ 8 คำต่ำกว่า 50% | 28 words: 11 above 75%, but 8 below 50% | ไอและหายใจได้ 0% |
| fig13r | คำไหนถูกสับสนกับคำไหน | Which words get confused with which | ไอถูกตอบเป็นน้ำมูกไหล 55% |

## A takeaway line for the bottom of the panel (modest, on our data)

TH: ในข้อมูลของเรา ความแม่นยำที่เสียไปส่วนใหญ่มาจากการเปลี่ยนผู้แสดง สิ่งที่ช่วยได้มากที่สุดคือการจัดการมือซ้าย–ขวา DANN ไม่ช่วย และเกณฑ์ความเชื่อมั่นต้องตั้งจากผู้แสดงอื่น ไม่ใช่จากการแบ่งสุ่ม

EN: On our data, most of the lost accuracy comes from changing the signer. The biggest help was handling left and right hands, DANN did not help, and the confidence threshold must be set from other signers, not from a random split.

## Notes
- Q4 and Q6 are the weakest answers (mixed, and exploratory). Keep their wording as written; do not upgrade them.
- "คุณ" is 100% in `fig2r` only because it was tested on S04 and S05 (50 clips); the card's footer says so.
- The paper's conclusion for DANN is "DANN did not help in any tested situation" (4.4); the poster line says the same.
