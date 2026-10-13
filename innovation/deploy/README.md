---
title: ThSL Bridge
emoji: 🤟
colorFrom: green
colorTo: blue
sdk: streamlit
app_file: streamlit_app.py
pinned: false
---

# ThSL Bridge — Thai Sign Language Recognition

อัปโหลดคลิปท่าภาษามือไทย 1 ท่า แล้วโมเดล Stacked LSTM + MediaPipe จะทำนายคำ

รองรับ 10 คำ: คนหูหนวก, คุณ, ช่วย, ขอบคุณ, ฉัน, ต้องการ, เข้าใจ, ไม่, ถาม, บอก

## โครงสร้าง
- วิดีโอ → MediaPipe (126 keypoint/เฟรม) → resample 30 เฟรม → LSTM → คำ

## ไฟล์ที่ต้องมี
- `app.py`
- `requirements.txt`
- `thsl_model_v6c.weights.h5`  (โมเดลที่เทรนแล้ว — อัปโหลดเข้า Space ด้วย)

## รันในเครื่อง
```bash
pip install -r requirements.txt
streamlit run app.py
```

Repo: https://github.com/Koten-1/ThSL-Bridge
