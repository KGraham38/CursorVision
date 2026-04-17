from pathlib import Path
import json
import numpy as np

try:
    import tensorflow as tf
except Exception:
    tf = None


FEATURE_NAMES = [
    "average_horizontal",
    "average_vertical",
    "look_horizontal",
    "look_vertical",
    "centered_x_norm",
    "centered_y_norm",
    "raw_target_x_norm",
    "raw_target_y_norm",
    "left_iris_x_norm",
    "left_iris_y_norm",
    "right_iris_x_norm",
    "right_iris_y_norm",
    "left_mid_x_norm",
    "left_mid_y_norm",
    "right_mid_x_norm",
    "right_mid_y_norm",
    "left_brow_x_norm",
    "left_brow_y_norm",
    "right_brow_x_norm",
    "right_brow_y_norm",
]


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _target_x_norm(sample):
    if "target_x_norm" in sample:
        return _safe_float(sample["target_x_norm"])
    if "screen_x_norm" in sample:
        return _safe_float(sample["screen_x_norm"])
    if "screem_x_norm" in sample:
        return _safe_float(sample["screem_x_norm"])
    return 0.0


def _target_y_norm(sample):
    if "target_y_norm" in sample:
        return _safe_float(sample["target_y_norm"])
    if "screen_y_norm" in sample:
        return _safe_float(sample["screen_y_norm"])
    if "screem_y_norm" in sample:
        return _safe_float(sample["screem_y_norm"])
    return 0.0


def build_training_arrays(samples):
    x_rows = []
    y_rows = []

    for sample in samples:
        feature_dict = sample.get("features", {})
        if not feature_dict:
            continue

        x_rows.append([_safe_float(feature_dict.get(name, 0.0)) for name in FEATURE_NAMES])
        y_rows.append([_target_x_norm(sample), _target_y_norm(sample)])

    if not x_rows:
        return None, None

    x_array = np.asarray(x_rows, dtype=np.float32)
    y_array = np.asarray(y_rows, dtype=np.float32)
    return x_array, y_array


def build_model(input_size):
    normalizer = tf.keras.layers.Normalization(axis=-1)

    model = tf.keras.Sequential([
        tf.keras.Input(shape=(input_size,)),
        normalizer,
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(2, activation="sigmoid"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",
        metrics=["mae"],
    )
    return model, normalizer


def train_and_save_model(samples, model_path):
    if tf is None:
        print("TensorFlow is not installed. Skipping training.")
        return None

    if not samples or len(samples) < 20:
        print("Not enough calibration samples to train model.")
        return None

    x_array, y_array = build_training_arrays(samples)
    if x_array is None or y_array is None or len(x_array) < 20:
        print("Not enough valid calibration samples to train model.")
        return None

    tf.keras.utils.set_random_seed(42)

    model, normalizer = build_model(len(FEATURE_NAMES))
    normalizer.adapt(x_array)

    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="loss",
        patience=10,
        restore_best_weights=True,
    )

    model.fit(
        x_array,
        y_array,
        epochs=100,
        batch_size=min(16, len(x_array)),
        verbose=0,
        callbacks=[early_stop],
    )

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))
    print(f"Gaze model saved to {model_path}")
    return model


def train_from_calibration_json(json_path, model_path=None):
    json_path = Path(json_path)
    with open(json_path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    samples = payload.get("data_values", [])

    if model_path is None:
        model_path = json_path.parent.parent / "models" / "gaze_smoother.keras"

    return train_and_save_model(samples, model_path)


def load_trained_model(model_path):
    if tf is None:
        print("TensorFlow is not installed. Live TF assist disabled.")
        return None

    model_path = Path(model_path)
    if not model_path.exists():
        print(f"No saved model found at {model_path}")
        return None

    try:
        model = tf.keras.models.load_model(str(model_path), compile=False)
        print(f"[TF] Loaded model from {model_path}")
        return model
    except Exception as exc:
        print(f"[TF] Failed to load model: {exc}")
        return None


def predict_target_norm(model, feature_dict):
    if model is None:
        return None

    try:
        x_array = np.asarray(
            [[_safe_float(feature_dict.get(name, 0.0)) for name in FEATURE_NAMES]],
            dtype=np.float32,
        )
        prediction = model.predict(x_array, verbose=0)[0]
        pred_x = float(np.clip(prediction[0], 0.0, 1.0))
        pred_y = float(np.clip(prediction[1], 0.0, 1.0))
        return pred_x, pred_y
    except Exception as exc:
        print(f"[TF] Prediction failed: {exc}")
        return None