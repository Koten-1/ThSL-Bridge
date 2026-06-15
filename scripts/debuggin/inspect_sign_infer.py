"""
Step 2 of 2 — run with: thsl_tf_env (has tensorflow)
Reads the .npy files saved by inspect_sign.py and runs model inference on them.

Usage: python scripts/inspect_sign_infer.py ช่วย
"""
import sys, os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
from pathlib import Path
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

SIGN    = sys.argv[1] if len(sys.argv) > 1 else "ช่วย"
OUT_DIR = Path(f"D:/KachornThSL/temp/inspect/{SIGN}")
PROC_DIR = Path(f"D:/KachornThSL/data/processed/{SIGN}")

TARGET_SIGNS = [
    "คนหูหนวก","คุณ","ช่วย","ขอบคุณ",
    "ฉัน","ต้องการ","เข้าใจ","ไม่","ถาม","บอก","finish","none"
]
SIGN_EN = {
    "คนหูหนวก":"deaf","คุณ":"you","ช่วย":"help","ขอบคุณ":"thank-you",
    "ฉัน":"I/me","ต้องการ":"want",
    "เข้าใจ":"understand","ไม่":"no/not","ถาม":"ask",
    "บอก":"tell","finish":"finish","none":"none",
}

model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),
    Dropout(0.5), LSTM(32), Dropout(0.5),
    Dense(16, activation="relu"), Dense(12, activation="softmax")
])
model.load_weights("D:/KachornThSL/models/thsl_model_v6c.weights.h5")

def infer(kp):
    pred = model.predict(np.expand_dims(kp, 0), verbose=0)[0]
    idx  = np.argmax(pred)
    top3 = sorted(range(len(pred)), key=lambda i: -pred[i])[:3]
    return TARGET_SIGNS[idx], float(pred[idx]), [(TARGET_SIGNS[i], float(pred[i])) for i in top3]

def row(label, kp):
    sign, conf, top3 = infer(kp)
    ok   = "✓" if sign == SIGN else "✗"
    t3   = "  |  ".join(f"{SIGN_EN.get(s,s)} {c:.0%}" for s,c in top3)
    zero = int(np.all(kp.reshape(30, 126) == 0, axis=1).sum())
    return ok, sign, conf, t3, zero

print(f"\n{'='*65}")
print(f"Model inference results for: {SIGN} ({SIGN_EN.get(SIGN,SIGN)})")
print(f"{'='*65}\n")
print(f"  {'File':<28} {'Result':<5} {'Predicted':<12} {'Conf':>6}  {'Zero':>5}  Top-3")
print(f"  {'-'*28} {'-'*5} {'-'*12} {'-'*6}  {'-'*5}  {'-'*30}")

correct_live = correct_saved = total_live = total_saved = 0

# Live re-extracted
for npy in sorted(OUT_DIR.glob("live_*.npy")):
    kp = np.load(npy)
    ok, sign, conf, t3, zero = row("live", kp)
    label = npy.stem.replace("live_", "")
    print(f"  [LIVE ] {label:<26} {ok}     {SIGN_EN.get(sign,sign):<12} {conf:>5.0%}  {zero:>3}/30  {t3}")
    total_live += 1
    if sign == SIGN: correct_live += 1

print()

# Saved processed .npy
for npy in sorted(PROC_DIR.glob("*.npy")):
    kp = np.load(npy)
    ok, sign, conf, t3, zero = row("saved", kp)
    print(f"  [SAVED] {npy.stem:<26} {ok}     {SIGN_EN.get(sign,sign):<12} {conf:>5.0%}  {zero:>3}/30  {t3}")
    total_saved += 1
    if sign == SIGN: correct_saved += 1

print(f"\nSummary:")
print(f"  Live re-extracted:  {correct_live}/{total_live} correct")
print(f"  Saved processed:    {correct_saved}/{total_saved} correct")

if correct_live < correct_saved:
    print("\n  ⚠  Live extraction is worse than saved — extraction pipeline may differ")
elif correct_live == correct_saved:
    print("\n  ✓  Live and saved match — extraction pipeline is consistent")
