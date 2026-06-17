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
- [x] keypoint_stream.py (state machine, stillness, DirectShow)
- [x] predict_stream.py (vote window, threshold, finish handling)
- [x] postprocess.py (Typhoon + gTTS, graceful degradation)
- [x] augment_keypoints.py (scale/translate/rotate, ทำไมปิด flip)
- [x] check_thresholds.py

---

## 9. keypoint_stream.py — State Machine + Stillness

### State Machine: 2 สถานะ

```
IDLE ──── (มือปรากฏ IDLE_WARMUP=4 เฟรมติดกัน) ────► COLLECTING
COLLECTING ── (stillness / มือหาย / ครบ MAX_COLLECT) ──► IDLE
```

- **IDLE_WARMUP = 4** กันทริกเกอร์จากมือผ่านจอเฉย ๆ
- **COLLECTING** เก็บเฉพาะเฟรมที่มีมือ (ตรงกับ extract_keypoints.py — แก้ปัญหา train/serve mismatch)

### Stillness Detection — "รู้ว่าท่าจบแล้ว"

```python
delta = np.mean(np.abs(keypoints_row - prev_kp))
if delta < STILL_THRESHOLD:   # 0.03
    still_counter += 1
else:
    still_counter = 0
if still_counter >= STILL_FRAMES:   # 6 เฟรมติดกัน ≈ 0.2s
    trigger = True
```

| พารามิเตอร์ | ค่า | ความหมาย |
|---|---|---|
| STILL_THRESHOLD | 0.03 | delta ต่ำกว่านี้ = นิ่ง |
| STILL_FRAMES | 6 | ต้องนิ่งติดกัน 6 เฟรม |
| MIN_COLLECT | 10 | เริ่มเช็ค stillness หลังได้ 10 เฟรม |
| MAX_COLLECT | 150 | safety cap — ส่งเลยหลัง 5 วินาที |
| MISSING_TOLERANCE | 8 | ทนมือหายได้ 8 เฟรม (กัน flicker) |

### Resampling — ปรับความเร็วให้ตรงตอนเทรน

```python
indices  = np.linspace(0, len(arr) - 1, 30, dtype=int)
keypoints = arr[indices]   # ดึง 30 index กระจายเท่ากัน
```

ทำท่าช้าหรือเร็วแค่ไหน → ก็ได้ 30 เฟรมเสมอ = ตรงกับ input shape โมเดล

### Finish Gesture — ยกมือทั้งสองข้างขึ้นสูง

```python
if lh_wrist_y < FINISH_THRESHOLD and rh_wrist_y < FINISH_THRESHOLD:
    # FINISH_THRESHOLD = 0.35 (y = 0 คือบนสุด, 1 คือล่างสุด)
    # ยก wrist ขึ้นสูงกว่า 35% จากบนจอ = trigger finish
```

เขียน `finish.txt` → predict_stream.py อ่านแล้วส่ง sentence ออก

### DirectShow Backend — ทำไมต้อง CAP_DSHOW

```python
cap = cv2.VideoCapture(SOURCE, cv2.CAP_DSHOW)
```

Windows ค่าเริ่มต้นใช้ MSMF backend → เปิดกล้องได้แต่ดึงเฟรมไม่ออก (error `-1072875772`)
DirectShow แก้ปัญหานี้ได้ ใช้เฉพาะ webcam — ไฟล์วิดีโอไม่ต้องการ

### IPC ระหว่าง 2 โปรเซส (ผ่าน temp files)

| ไฟล์ | ทิศทาง | ข้อมูล |
|---|---|---|
| `keypoints.npy` | stream → predict | 30×126 keypoints |
| `finish.txt` | stream → predict | สัญญาณจบประโยค |
| `result.txt` | predict → stream | ผลลัพธ์แสดงบนหน้าจอ |
| `topn.json` | predict → stream | top-5 scores สำหรับ UI bars |

---

## 10. predict_stream.py — Vote Window + Threshold + Finish

### SIGN_THRESHOLDS — Confidence แต่ละคำไม่เท่ากัน

```python
SIGN_THRESHOLDS = {
    "คนหูหนวก": 0.70,   # correct=0.96 — safe ลด threshold ได้
    "คุณ":      0.60,   # BROKEN: wrong > correct (0.71 > 0.69) — ลด threshold กันค้าง
    "ช่วย":     0.65,   # BROKEN: wrong > correct (0.91 > 0.80) — threshold แก้ไม่ได้ 100%
    "ขอบคุณ":   0.80,   # perfect: correct=1.00, wrong=0.00
    ...
}
```

> **กฎ:** threshold ควรอยู่ระหว่าง `wrong_conf` กับ `correct_conf`
> ถ้า `wrong > correct` (BROKEN) → threshold ช่วยลดได้บ้างแต่ไม่ได้แก้รากเหง้า → ต้องเก็บข้อมูลเพิ่ม / retrain

### Vote Window Logic

```python
VOTE_WINDOW = 3   # เก็บ prediction ล่าสุด 3 ครั้ง (deque)
VOTE_NEEDED = 1   # ยืนยันได้ทันทีหากมั่นใจ 1 ครั้ง
```

**ทำไม VOTE_NEEDED = 1?** keypoint_stream.py ส่งครั้งละ 1 ท่าที่สมบูรณ์แล้ว → ไม่ต้องรอ vote หลายครั้ง
(ก่อนหน้านี้ต้องรอ 3 ครั้ง ตอนที่ stream ส่งทีละเฟรม)

```python
vote_entry = sign if (confidence >= threshold and sign != "none") else "none"
recent_predictions.append(vote_entry)

non_none = [s for s in recent_predictions if s != "none"]
top_sign  = max(set(non_none), key=non_none.count)
top_count = non_none.count(top_sign)

if top_count >= VOTE_NEEDED:   # → CONFIRMED
elif top_count > 0:             # → BUILDING
else:                           # → none (ทั้งหมดคือ none)
```

### 3 สถานะผลลัพธ์

| สถานะ | ความหมาย | แสดงบน UI |
|---|---|---|
| CONFIRMED | top_count ≥ VOTE_NEEDED | `คำ (95%)` + เพิ่ม buffer |
| BUILDING | top_count > 0 แต่ยังไม่ถึง | `? คำ (80%) [1/3]` |
| none | confidence ต่ำกว่า threshold | `...` |

### Finish Handling — 2 วิธี

```
1. finish.txt  (gesture: ยกมือ 2 ข้าง) — keypoint_stream เขียน
2. "finish" class — โมเดลทาย finish เอง
```

ทั้ง 2 วิธีทำเหมือนกัน: ส่ง word_buffer ไป postprocess.process() ใน background thread แล้ว clear buffer

### Duplicate Prevention

```python
elif not word_buffer or word_buffer[-1] != top_sign:
    word_buffer.append(top_sign)   # เพิ่มเฉพาะถ้าต่างจากคำก่อน
else:
    print(f"  dup: {conf_en}")     # คำซ้ำ — ไม่เพิ่ม
```

---

## 11. postprocess.py — Typhoon LLM + gTTS + Graceful Degradation

### Pipeline

```
word_buffer → build_sentence() → speak()
               (Typhoon API)      (gTTS → mp3 → เล่นเสียง)
```

### Graceful Degradation — ล้มไม่พัง

| เหตุการณ์ | ผลลัพธ์ |
|---|---|
| ไม่มี API key / ไม่มีเน็ต | ใช้คำดิบ join ด้วยเว้นวรรค |
| Typhoon timeout/error | ใช้คำดิบ (fallback เดียวกัน) |
| gTTS ล้มเหลว | print แทน — โปรแกรมไม่หยุด |

### Typhoon — Thai LLM เรียบเรียงประโยค

```python
prompt = (
    "คุณเป็นผู้ช่วยแปลงคำจากภาษามือไทยให้เป็นประโยคภาษาไทยที่เป็นธรรมชาติ "
    "ตอบกลับเฉพาะประโยคเท่านั้น ห้ามอธิบายเพิ่ม\n"
    f"คำ: {raw}"
)
# model: typhoon-v2.5-30b-a3b-instruct
# max_tokens: 100, temperature: 0.3 (ตอบตรง ไม่สร้างสรรค์เกินไป)
```

### ทำไมใช้ timestamp ในชื่อไฟล์ mp3

```python
mp3 = os.path.join(TTS_DIR, f"tts_{int(time.time()*1000)}.mp3")
```

**ปัญหา:** ถ้าใช้ชื่อเดิมซ้ำ แล้ว media player ยังเปิดค้างอยู่ → `Permission denied`
**แก้:** ชื่อใหม่ทุกครั้ง → player เก่ายังเล่นไฟล์เก่าอยู่ ไม่กระทบไฟล์ใหม่

```python
def _cleanup_old_tts(keep_latest=3):
    # ลบไฟล์เก่า เก็บแค่ 3 อัน (best-effort — ข้าม locked files)
```

### วิธีหา API Key (2 แหล่ง, ลำดับ)

```
1. os.environ.get("TYPHOON_API_KEY")   ← env var
2. scripts/typhoon_key.txt             ← ไฟล์ text (1 บรรทัด)
```

---

## 12. augment_keypoints.py — Scale / Translate / Rotate (ปิด Flip)

### 3 Augmentation (random 50% chance แต่ละอัน)

```python
# Rotate ±15°: หมุน x,y ด้วย rotation matrix
rotated[:, 0::3] = cos_a * x - sin_a * y   # x ใหม่
rotated[:, 1::3] = sin_a * x + cos_a * y   # y ใหม่

# Scale ×0.85 ถึง ×1.15: ยืด/หดทั้งท่า (มือใกล้/ไกลกล้อง)
return np.clip(sequence * scale, 0.0, 1.0)

# Translate ±10%: เลื่อนซ้าย-ขวา-บน-ล่าง (ตำแหน่งมือในเฟรม)
return np.clip(sequence + shift, 0.0, 1.0)
```

### ทำไม **ปิด** augment_flip?

```python
# augment_flip ถูก define แต่ไม่ถูกเรียก — ตั้งใจปิด
flipped[:, 0::3] = 1 - flipped[:, 0::3]   # สะท้อนแกน x
```

**เหตุผล:** ภาษามือมีทิศทาง

```
คุณ  = ชี้ออกจากตัว → mirror → ชี้เข้าหาตัว = ฉัน ← คนละความหมาย!
```

flip จะสับสน label: `คุณ` กลายเป็นหน้าตาคล้าย `ฉัน` แต่ยังติด label `คุณ` → โมเดลงง

> **กฎ:** rotate/scale/translate ปลอดภัย (ไม่เปลี่ยนทิศทางสัมพัทธ์ของมือ)
> flip ไม่ปลอดภัยสำหรับ directional signs

### ผลลัพธ์ที่ได้

```
1 ต้นฉบับ × 5 augments = 6 ไฟล์ต่อคลิป
444 ต้นฉบับ × 5 = 2,220 augmented
รวม 2,664 (ตรงกับตัวเลขใน section 6)
```

- `seed=42` → reproducible — run ซ้ำได้ผลเดิม
- Skip ถ้าไฟล์มีอยู่แล้ว (idempotent — run ซ้ำปลอดภัย)

---

## 13. check_thresholds.py — เครื่องมือ Calibrate หลัง Retrain

### วัตถุประสงค์

หลัง retrain โมเดลทุกครั้ง → run สคริปต์นี้ → ได้ตาราง → อัปเดต `SIGN_THRESHOLDS` ใน predict_stream.py

### วิธีทำงาน

```python
for sign in TARGET_SIGNS:
    files = list(folder.glob('*.npy'))[:20]   # ทดสอบ 20 ไฟล์แรก
    for f in files:
        pred = model.predict(...)
        idx  = np.argmax(pred[0])
        conf = float(pred[0][idx])
        if predicted == sign and conf >= threshold:
            above += 1   # ผ่าน threshold
```

### Output ที่ได้

```
Sign           Thr   Pass%   AvgConf   MaxConf  Status
--------------------------------------------------------------
คนหูหนวก     0.70    100%      0.96      0.99  OK
คุณ           0.60     40%      0.68      0.82  LOW
ช่วย          0.65     30%      0.72      0.91  LOW
ขอบคุณ        0.80    100%      1.00      1.00  OK
...
```

| Status | เงื่อนไข | ความหมาย |
|---|---|---|
| OK | pass% ≥ 50% | threshold ใช้ได้ |
| LOW | 0% < pass% < 50% | threshold สูงเกิน หรือโมเดลยังอ่อน |
| BLOCKED | pass% = 0% | threshold ปิดคำนั้นทั้งหมด — ต้องลด |

### Workflow หลัง Retrain

```
1. เทรนโมเดลใหม่ → บันทึก .weights.h5
2. run check_thresholds.py → ดู Pass% และ AvgConf ของแต่ละ sign
3. ปรับ SIGN_THRESHOLDS ใน predict_stream.py ให้ Pass% ≥ 70-80%
4. test live ด้วย keypoint_stream + predict_stream
```

> **หลักการตั้ง threshold:** ตั้งให้ `wrong_conf < threshold < correct_conf`
> ถ้า wrong_conf ≥ correct_conf (BROKEN) → threshold ช่วยได้จำกัด → ต้องเก็บข้อมูลเพิ่ม/retrain ใหม่

