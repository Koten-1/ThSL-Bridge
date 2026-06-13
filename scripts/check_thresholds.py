import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from pathlib import Path

TARGET_SIGNS = ['คนหูหนวก','คุณ','ช่วย','ขอบคุณ','ฉัน','ต้องการ','เข้าใจ','ไม่','ถาม','บอก','finish','none']
SIGN_THRESHOLDS = {
    'คนหูหนวก': 0.82, 'คุณ': 0.97, 'ช่วย': 0.92, 'ขอบคุณ': 0.92,
    'ฉัน': 0.75, 'ต้องการ': 0.83, 'เข้าใจ': 0.83,
    'ไม่': 0.73, 'ถาม': 0.76, 'บอก': 0.80, 'finish': 0.80, 'none': 0.95
}

model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),
    Dropout(0.5), LSTM(32), Dropout(0.5),
    Dense(16, activation='relu'), Dense(12, activation='softmax')
])
model.load_weights('D:/KachornThSL/models/thsl_model_v6c.weights.h5')
print("Model loaded.\n")

print(f"{'Sign':<14} {'Thr':>5}  {'Pass%':>6}  {'AvgConf':>8}  {'MaxConf':>8}  Status")
print('-' * 58)

for sign in TARGET_SIGNS:
    folder = Path(f'D:/KachornThSL/data/processed/{sign}')
    if not folder.exists():
        folder = Path(f'D:/KachornThSL/data/augmented/{sign}')
    if not folder.exists():
        print(f'{sign:<14}  no data folder found')
        continue

    files = list(folder.glob('*.npy'))[:20]
    if not files:
        print(f'{sign:<14}  no .npy files')
        continue

    total = above = 0
    confs = []

    for f in files:
        try:
            kp = np.load(f)
            if kp.shape != (30, 126):
                continue
            pred = model.predict(np.expand_dims(kp, 0), verbose=0)
            idx = np.argmax(pred[0])
            conf = float(pred[0][idx])
            predicted = TARGET_SIGNS[idx]
            total += 1
            confs.append(conf)
            if predicted == sign and conf >= SIGN_THRESHOLDS[sign]:
                above += 1
        except Exception as e:
            pass

    if total == 0:
        print(f'{sign:<14}  could not load files')
        continue

    avg = sum(confs) / len(confs)
    mx  = max(confs)
    pct = above / total * 100
    status = 'OK' if pct >= 50 else ('LOW' if pct > 0 else 'BLOCKED')
    print(f'{sign:<14} {SIGN_THRESHOLDS[sign]:>5.2f}  {pct:>6.0f}%  {avg:>8.2f}  {mx:>8.2f}  {status}')
