import numpy as np
from pathlib import Path

RAW_DIR = Path("D:/KachornThSL/data/processed")
AUG_DIR = Path("D:/KachornThSL/data/augmented")
AUG_DIR.mkdir(parents=True, exist_ok=True)

NUM_AUGMENTS = 5
RNG = np.random.default_rng(seed=42)

def augment_scale(sequence):
    scale = RNG.uniform(0.85, 1.15)
    return np.clip(sequence * scale, 0.0, 1.0)

def augment_translate(sequence):
    # shift by ±10% in any direction
    shift = RNG.uniform(-0.1, 0.1)
    return np.clip(sequence + shift, 0.0, 1.0)

def augment_flip(sequence):
    flipped = sequence.copy()
    flipped[:, 0::3] = 1 - flipped[:, 0::3]
    return flipped

def augment_rotate(sequence):
    angle = RNG.uniform(-15, 15)
    angle_rad = np.deg2rad(angle)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    
    rotated = sequence.copy()
    x = sequence[:, 0::3]
    y = sequence[:, 1::3]
    
    rotated[:, 0::3] = cos_a * x - sin_a * y
    rotated[:, 1::3] = sin_a * x + cos_a * y
    
    return np.clip(rotated, 0.0, 1.0)

for sign_dir in RAW_DIR.iterdir():
    if not sign_dir.is_dir():
        continue
    
    sign_name = sign_dir.name
    out_dir = AUG_DIR / sign_name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for npy_file in sign_dir.glob("*.npy"):
        sequence = np.load(str(npy_file))
        
        for i in range(NUM_AUGMENTS):
            augmented_sequence = sequence.copy()

            # NOTE: flip (horizontal mirror) is intentionally disabled — it corrupts
            # directional signs like คุณ (point away) vs ฉัน (point at self).
            if RNG.random() > 0.5:
                augmented_sequence = augment_rotate(augmented_sequence)
            if RNG.random() > 0.5:
                augmented_sequence = augment_scale(augmented_sequence)
            if RNG.random() > 0.5:
                augmented_sequence = augment_translate(augmented_sequence)

            aug_file_name = f"{npy_file.stem}_aug_{i}.npy"
            out_file_path = out_dir / aug_file_name

            if out_file_path.exists():
                print(f"  [skip] {aug_file_name}")
                continue

            np.save(str(out_file_path), augmented_sequence)
            print(f"  ✓ {aug_file_name}")

