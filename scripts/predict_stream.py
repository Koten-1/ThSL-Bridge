import numpy as np
import time
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

TARGET_SIGNS = [
    "คนหูหนวก (Deaf)", "คุณ (You)", "ช่วย (Help)", "ขอบคุณ (Thanks)",
    "คำถาม (Question)", "ฉัน (Me)", "ต้องการ (Want)", "เข้าใจ (Understand)", 
    "ไม่ (No)", "ถาม (Ask)"
]

KEYPOINTS_PATH = "D:/KachornThSL/temp/keypoints.npy"


model = Sequential([
    LSTM(32, return_sequences=True, input_shape=(30, 126)),
    Dropout(0.5),
    LSTM(32),
    Dropout(0.5),
    Dense(16, activation='relu'),
    Dense(10, activation='softmax')
])

model.load_weights("D:/KachornThSL/models/thsl_model_v3.weights.h5")
print("Model loaded!")

last_modified = 0

while True:
    if os.path.exists(KEYPOINTS_PATH):
        modified = os.path.getmtime(KEYPOINTS_PATH)
        if modified > last_modified:
            last_modified = modified
            
            keypoints = np.load(KEYPOINTS_PATH)
            keypoints = np.expand_dims(keypoints, axis=0)  # add batch dimension
            
            prediction = model.predict(keypoints, verbose=0)
            predicted_idx = np.argmax(prediction)
            confidence = prediction[0][predicted_idx]
            
            if confidence > 0.80:
                result = f"{TARGET_SIGNS[predicted_idx]} ({confidence:.0%})"
                print(f"Sign: {result}")
            else:
                result = "..."
                print(result)

            with open("D:/KachornThSL/temp/result.txt", "w", encoding="utf-8") as f:
                f.write(result)
    
    time.sleep(0.5)