from pathlib import Path
import json
import numpy as np
import tensorflow as tf
from tensorflow_model import FEATURE_NAMES

project_root = Path(__file__).resolve().parent
json_path = project_root / "calibration_data.json"
model_path = project_root.parent / "models" / "gaze_smoother.keras"

print("Calibration JSON exists:", json_path.exists())
print("Model exists:", model_path.exists())

if not json_path.exists():
    raise FileNotFoundError(f"Missing {json_path}")

if not model_path.exists():
    raise FileNotFoundError(f"Missing {model_path}")

with open(json_path, "r", encoding="utf-8") as f:
    payload = json.load(f)

samples = payload.get("data_values", [])
if not samples:
    raise ValueError("No calibration samples found.")

sample = samples[0]
features = sample["features"]

x = np.asarray([[float(features.get(name, 0.0)) for name in FEATURE_NAMES]], dtype=np.float32)

model = tf.keras.models.load_model(model_path)
prediction = model.predict(x, verbose=0)[0]

print("Prediction x_norm:", float(prediction[0]))
print("Prediction y_norm:", float(prediction[1]))
print("Prediction complete.")