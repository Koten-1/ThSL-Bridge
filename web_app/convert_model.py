"""Convert thsl_model_v6c → TensorFlow.js (for in-browser inference)."""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import tensorflowjs as tfjs

model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),
    Dropout(0.5), LSTM(32), Dropout(0.5),
    Dense(16, activation="relu"), Dense(12, activation="softmax"),
])
model.load_weights("D:/KachornThSL/models/thsl_model_v6c.weights.h5")

out = "D:/KachornThSL/web_app/model"
tfjs.converters.save_keras_model(model, out)
print(f"saved TF.js model to: {out}")
