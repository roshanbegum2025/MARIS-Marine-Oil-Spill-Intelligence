"""
Evaluate the trained oil-spill classifier on the REAL held-out test set.
This produces the true accuracy/precision/recall/F1 numbers for your dashboard —
no invented numbers. Run this once after training, before building anything
that displays "model accuracy" anywhere.

Usage (from the oil-spill-project root folder):
    .\venv311\Scripts\python.exe src\evaluate_model.py
"""

import json
import os
import numpy as np
import tensorflow as tf

# ==============================
# PATHS
# ==============================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "oil_spill_final.keras")
TEST_DIR = os.path.join(PROJECT_ROOT, "data", "test")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# ==============================
# LOAD MODEL + TEST DATA
# ==============================
print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)

test_data = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False,
)

class_names = test_data.class_names  # e.g. ['no-oil-spill', 'oil-spill']
print("Classes:", class_names)

# ==============================
# RUN PREDICTIONS
# ==============================
y_true = []
y_pred = []
y_prob = []

for images, labels in test_data:
    probs = model.predict(images, verbose=0).flatten()
    preds = (probs >= 0.5).astype(int)
    y_true.extend(labels.numpy().tolist())
    y_pred.extend(preds.tolist())
    y_prob.extend(probs.tolist())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

# ==============================
# METRICS (computed by hand, no sklearn dependency needed)
# ==============================
tp = int(np.sum((y_pred == 1) & (y_true == 1)))
tn = int(np.sum((y_pred == 0) & (y_true == 0)))
fp = int(np.sum((y_pred == 1) & (y_true == 0)))
fn = int(np.sum((y_pred == 0) & (y_true == 1)))

total = len(y_true)
accuracy = (tp + tn) / total if total else 0
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

metrics = {
    "model_file": os.path.basename(MODEL_PATH),
    "class_names": class_names,
    "test_set_size": total,
    "confusion_matrix": {
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
    },
    "accuracy": round(accuracy, 4),
    "precision": round(precision, 4),
    "recall": round(recall, 4),
    "f1_score": round(f1, 4),
}

out_path = os.path.join(RESULTS_DIR, "metrics.json")
with open(out_path, "w") as f:
    json.dump(metrics, f, indent=2)

print("\n" + "=" * 40)
print("REAL TEST SET RESULTS (no estimates)")
print("=" * 40)
for k, v in metrics.items():
    print(f"{k}: {v}")
print(f"\nSaved to: {out_path}")
print("This file is what your dashboard's Reports page will read.")
