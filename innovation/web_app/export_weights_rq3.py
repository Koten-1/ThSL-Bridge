"""Export RQ3 comparison-demo weights to JSON (no tensorflowjs needed) — rebuilt in TF.js.

Companion to export_weights.py, for the "compare models" mode (Baseline vs DANN, 10-way,
no finish/none). Run this AFTER downloading rq3_pooled_baseline.weights.h5 and
rq3_pooled_dann_signonly.weights.h5 from Colab (see the export cell in
research/notebooks/🧩RQ3_DANN.ipynb) and placing them next to this script.

Both source files are already single-output, 10-class Sequential-compatible weights --
the DANN model's auxiliary signer head was already stripped inside the notebook's
export cell (transplanted into a plain build_baseline_model()-shaped model before
saving), so no special-casing is needed here.
"""
import os
import json

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

HERE = os.path.dirname(os.path.abspath(__file__))


def build_ten_class_model():
    return Sequential([
        LSTM(32, return_sequences=True, input_shape=(30, 126)),
        Dropout(0.5), LSTM(32), Dropout(0.5),
        Dense(16, activation="relu"), Dense(10, activation="softmax"),
    ])


def export_one(weights_h5, out_json):
    model = build_ten_class_model()
    model.load_weights(weights_h5)
    weights = model.get_weights()
    out = [{"shape": list(w.shape), "data": w.flatten().tolist()} for w in weights]
    with open(out_json, "w") as f:
        json.dump(out, f)
    print(f"{os.path.basename(weights_h5)} -> {os.path.basename(out_json)}  ({len(weights)} weight arrays)")


if __name__ == "__main__":
    export_one(
        os.path.join(HERE, "rq3_pooled_baseline.weights.h5"),
        os.path.join(HERE, "weights_rq3_baseline.json"),
    )
    export_one(
        os.path.join(HERE, "rq3_pooled_dann_signonly.weights.h5"),
        os.path.join(HERE, "weights_rq3_dann.json"),
    )
