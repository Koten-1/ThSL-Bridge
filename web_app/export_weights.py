"""Export model weights to JSON (no tensorflowjs needed) — rebuilt in TF.js."""
import os, json
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),
    Dropout(0.5), LSTM(32), Dropout(0.5),
    Dense(16, activation="relu"), Dense(12, activation="softmax"),
])
model.load_weights("D:/KachornThSL/models/thsl_model_v6c.weights.h5")

# get_weights() returns arrays in layer order:
# LSTM1: kernel, recurrent_kernel, bias
# LSTM2: kernel, recurrent_kernel, bias
# Dense1: kernel, bias ; Dense2: kernel, bias
weights = model.get_weights()
out = [{"shape": list(w.shape), "data": w.flatten().tolist()} for w in weights]

with open("D:/KachornThSL/web_app/weights.json", "w") as f:
    json.dump(out, f)

print(f"exported {len(weights)} weight arrays")
for i, w in enumerate(weights):
    print(f"  [{i}] shape={w.shape}")
