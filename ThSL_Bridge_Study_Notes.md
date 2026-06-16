# ThSL Bridge — Study Notes (สำหรับสไลด์ + ทบทวน)

> รวมโน้ตจาก learn_01, learn_02, somegoodmodel + คำอธิบายทั้งหมด
> วิธีเปิดบน iPad: วางไฟล์นี้ใน OneDrive/Google Drive หรืออีเมลหาตัวเอง

---

## 0. ภาพรวม Pipeline

```
ทำท่ามือ → กล้อง → MediaPipe (126 keypoint/เฟรม) → เก็บเฉพาะเฟรมมีมือ จนหยุดนิ่ง
→ บีบเหลือ 30 เฟรม → LSTM ทำนายท่า → เช็คความมั่นใจ + ยืนยัน
→ สะสมเป็นประโยค → ท่า finish → Typhoon เรียบเรียง → gTTS พูดออกเสียง
```

**ประเภทงาน:** Sequence Classification → เฉพาะคือ Isolated Sign Language Recognition (ISLR)
**วิธีเรียนรู้:** Supervised Learning (label ครบทุกคลิป จากชื่อโฟลเดอร์)
**สถาปัตยกรรม:** Stacked LSTM (สร้างเอง from scratch ไม่ใช่ transfer learning)

---

## 1. inspect_sign.py — เปรียบเทียบ keypoint เก่า vs ใหม่
### (จาก learn_01)

หัวใจอยู่ที่ **ตำแหน่ง `append` ว่าอยู่ใน `if` หรือนอก `if`**

```python
# ❌ ของเก่า (พัง) — append อยู่ "นอก" if
if results.multi_hand_landmarks:
    lh, rh = ...                          # มีมือ → ใส่ค่าจริง
frames.append(np.concatenate([lh, rh]))  # ← นอก if! เก็บทุกเฟรม รวมเฟรม 0

# ✅ ของใหม่ (แก้แล้ว) — append อยู่ "ใน" if
if results.multi_hand_landmarks:
    lh, rh = ...
    frames.append(np.concatenate([lh, rh]))  # ← ใน if! เก็บเฉพาะเฟรมมีมือ
```

- inspect_sign.py **จงใจใช้วิธีเก่า (นอก if)** เพื่อ "จำลอง" บั๊กเดิม
- keypoint_stream.py (ใหม่) เก็บเฉพาะเฟรมมีมือ จนหยุดนิ่ง

```python
if hand_present:
    collected.append(keypoints_row)   # เก็บเฉพาะเฟรมมีมือ (เหมือน extract ใหม่)
    # ...ตรวจว่าหยุดนิ่งหรือยัง → ถ้านิ่งก็จบ
```

### ใช้ inspect ทำอะไรได้บ้าง (2 อย่าง)
1. **พิสูจน์ว่าคลิป scrape ใช้ไม่ได้** → วัด `hand_pct = hand_count / total_frames * 100`
   - คลิปเราเอง: 100% | คลิป scrape: 29-62% (ต่ำ = MediaPipe จับมือไม่ได้ = ใช้ไม่ได้)
2. **เช็ค train/serve mismatch** → เทียบ keypoint ที่ดึงแบบ live (เก่า, มีเฟรม 0) กับข้อมูลเทรน (ใหม่, สะอาด)

### ⚠️ จำให้แม่น (กันเขียนผิด)
> **การแก้ = "ตัดเฟรมที่ไม่มีมือออก" ไม่ใช่ "เอาเข้ามา"**
> เฟรมไม่มีมือ = ค่า 0 ล้วน = ขยะ → ยิ่งมีเยอะยิ่งพัง

---

## 2. Data Leakage — group split เก่า vs ใหม่
### (จาก learn_02)

```python
# ❌ OLD (no group split — data leak)
for folder in ["processed", "augmented"]:        # ← โหลดรวมกันทั้งคู่
    ...append ทุกไฟล์...
X_train, X_test = train_test_split(X, y, ...)    # ← แบ่งหลังผสมแล้ว → รั่ว!
```

**ทำไมรั่ว:** คลิป `คุณ_1` + augment 5 อัน หน้าตาคล้ายกันมาก พอแบ่งสุ่ม:
```
TRAIN: คุณ_1_aug_0, aug_2, aug_3
TEST:  คุณ_1_aug_4   ← ฝาแฝดของ aug_2 ที่อยู่ใน train! (ควรอยู่ train ไม่ใช่ test)
```
→ โมเดลเหมือน "เคยเห็นข้อสอบ" → accuracy สูงปลอม **99.6%**

```python
# ✅ NEW (group-aware — honest)
# 1) เก็บเฉพาะคลิปต้นฉบับ (processed)
# 2) แบ่งต้นฉบับก่อน
train_orig, test_orig = train_test_split(originals, test_size=0.2, ...)
# 3) TEST = ต้นฉบับล้วน
# 4) TRAIN = ต้นฉบับ train + augment ของมันเท่านั้น
```

**กฎ:**
```
ถ้า คุณ_1 → TRAIN: คุณ_1 + aug_0..aug_4 ไป TRAIN ทั้งหมด
ถ้า คุณ_1 → TEST:  เอาแค่ คุณ_1 (ต้นฉบับ) ไป TEST — ไม่เอา augment
```
→ accuracy จริง **98.88%** | test set เหลือ 89 (ต้นฉบับล้วน)

> โมเดล**ไม่เปลี่ยนเลย** เปลี่ยนแค่ "วิธีแบ่ง" → 99.6% ปลอม กลายเป็น 98.88% จริง

---

## 3. Model — Stacked LSTM
### (เติมส่วนที่ somegoodmodel ยังว่าง)

```python
model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),  # ชั้น 1: การเคลื่อนไหวย่อย
    Dropout(0.5),
    LSTM(32),                                                # ชั้น 2: รวมเป็นรูปแบบท่า
    Dropout(0.5),
    Dense(16, activation='relu'),
    Dense(12, activation='softmax')                          # 12 ท่า
])
```

### ทำไม LSTM?
- ภาษามือ = ลำดับการเคลื่อนไหวตามเวลา → ต้องมี "ความจำ" → LSTM
- มี 3 ประตู: Forget (ลืมข้อมูลเก่า) / Input (เก็บข้อมูลใหม่) / Output (ส่งผลออก)
- งานวิจัยที่อ้างอิง (Springer 2024) สรุปว่า LSTM ดีสุดในกลุ่ม RNN/Bi-LSTM/FNN-LSTM

### ทำไม Stacked (2 ชั้น)?
- ชั้น 1 (`return_sequences=True`) เรียนการเคลื่อนไหวย่อย → ส่ง "ทั้ง 30 เฟรม" ต่อ
- ชั้น 2 รวมเป็นรูปแบบท่าทั้งท่า
- เหมือน: ตัวอักษร → คำ → ประโยค
- ต่างจาก LSTM ชั้นเดียว: ซับซ้อนกว่า เรียนรู้เป็นลำดับชั้น แต่เสี่ยง overfit มากกว่า → คุมด้วย 32 ยูนิต + Dropout 0.5

### ทำไม "from scratch" ไม่ใช่ transfer learning?
- input เป็น keypoint (126 ตัวเลข) ไม่ใช่รูปภาพ → โมเดล pre-trained รูปภาพใช้ไม่ได้
- ไม่มีโมเดล pre-trained สำหรับ keypoint sequence ของภาษามือไทย
- ข้อมูลน้อย งานเฉพาะ → LSTM เล็ก ๆ เหมาะสุด

### การเทรน
- **Gradient Descent + Backpropagation** (วน: ทำนาย → วัด loss → ปรับน้ำหนัก)
- `optimizer='adam'` (ปรับ learning rate อัตโนมัติ)
- `loss='sparse_categorical_crossentropy'` (จำแนกหลายคลาส, label เป็น integer)
- `EarlyStopping(patience=20, restore_best_weights=True)` → หยุดเมื่อ val_loss ไม่ดีขึ้น เก็บตัวดีสุด
- หยุดที่ epoch 93, best val_accuracy = **98.88%**

---

## 4. Train/Serve Mismatch — 3 Axis ที่ทำให้พัง

| Axis | เก่า (พัง) | ใหม่ (แก้) | ผล |
|---|---|---|---|
| 1. เฟรม 0 | เก็บเฟรมไม่มีมือด้วย | **ตัดเฟรม 0 ออก** | แก้ "อะไรก็เป็น help" |
| 2. ช่วงที่เก็บ | เอา 30 เฟรมแรกดิบ ๆ | เก็บทั้งท่าจนนิ่ง | ได้ท่าครบ |
| 3. ความเร็ว | ไม่ resample | resample เหลือ 30 (linspace) | ความเร็วตรงตอนเทรน |

**หลักการเดียว:** keypoint_stream.py ต้องดึง keypoint **เหมือน** extract_keypoints.py เป๊ะ

### บั๊ก ขอบคุณ ซ้ำ ๆ
- softmax ต้องเลือกคลาสเสมอ → input ว่าง (ไม่มีมือ = ค่า 0) → ทายเป็น ขอบคุณ
- เพราะ ขอบคุณ มีเฟรม 0 ในข้อมูลเทรนเยอะสุด → โมเดลเรียนว่า "เฟรม 0 เยอะ = ขอบคุณ"
- แก้ด้วย: ตัดเฟรม 0 + คลาส none + vote window

---

## 5. EDA (Exploratory Data Analysis)

| การวิเคราะห์ | คำถาม | นำไปสู่การตัดสินใจ |
|---|---|---|
| Class balance | ข้อมูลสมดุลไหม | 40/คำ ไม่ต้อง oversample |
| Hand-detection % | คลิปคุณภาพดีไหม | ลบ scraped (29%) |
| none vs คุณ overlap | ท่าไหนคล้ายกันอันตราย | distance 1.55 → ทำนายว่า คุณ จะสับสน |
| Static vs Motion | ท่าแบบไหน | เทคนิคยกมือขึ้น-ลง |
| Zero-frame | ข้อมูลสะอาดแค่ไหน | แก้ extraction |

⭐ ดาวเด่น: **none vs คุณ distance 1.55** — EDA ที่ "ทำนาย" บั๊กล่วงหน้า

---

## 6. ตัวเลขสำคัญ

| | จำนวน |
|---|---|
| Processed (ต้นฉบับ) | 444 |
| Augmented (×5) | 2,220 |
| **รวม** | **2,664** |
| Train (group-aware) | 2,130 |
| Test (ต้นฉบับล้วน) | 89 |
| Test Accuracy | **98.88%** |
| คลาส | 12 (10 คำ + none + finish) |

---

## 7. Defense Prep — 3-Move Structure

ทุกคำถามจะตกอยู่ใน 1 ใน 3 ข้อนี้:
1. **เขางานทำอะไร** — งานวิจัยเทียบโมเดล สรุป LSTM ดีสุด (4 คำ COVID)
2. **เราต่างยังไง + ทำไม** — เราต่อยอดเป็นระบบใช้งานจริง (ประโยค + เสียง + deploy)
3. **ข้อจำกัด + แผนต่อ** — 12 คำ, ผู้ทำคนเดียว; อนาคต: เพิ่มคนอัด, เพิ่มคำ, เทียบโมเดลเอง

> เจอคำถาม → ถามตัวเอง "นี่คือ Move 1, 2 หรือ 3?" แล้วตอบ move นั้น → ไม่ blank

**อย่าพูดคำว่า "just"** — เราไม่ได้ "แค่" ทำอะไร เราเอาผลวิจัยมาสร้างเป็นเครื่องมือใช้จริง (systems/application contribution)

---

## 8. บทเรียนหลัก (Meta-Lessons)
1. **กำหนดประเภทปัญหาก่อน** — Sequence ≠ Image
2. **ข้อมูลสำคัญกว่าโมเดล** — ทุกปัญหาคือข้อมูล (scraped, zero-frame, leakage)
3. **อย่าเชื่อผลที่ดีเกินไป** — 99.6% ทำให้สงสัย → เจอ leakage
4. **สร้างเครื่องมือดูข้อมูล** — inspect_sign.py เจอบั๊กที่อ่านโค้ดเฉย ๆ ไม่เจอ
5. **train/serve ต้องเหมือนกัน** — โมเดลต้องเห็นข้อมูลแบบเดียวกันตอนเทรนและตอนใช้
6. **ความซื่อสัตย์ = จุดแข็ง** — 98.88% (ไม่ใช่ 99.6%), ยอมรับ domain shift

---

## TODO — ไฟล์ที่ยังไม่ได้ทำโน้ต
- [ ] keypoint_stream.py (state machine, stillness, DirectShow)
- [ ] predict_stream.py (vote window, threshold, finish handling)
- [ ] postprocess.py (Typhoon + gTTS, graceful degradation)
- [ ] augment_keypoints.py (scale/translate/rotate, ทำไมปิด flip)
- [ ] check_thresholds.py
```
