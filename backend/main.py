"""
MARIS backend — minimal, real, honest.

Serves:
  GET  /metrics   -> real test-set metrics from results/metrics.json
                      (run src/evaluate_model.py first to generate this)
  POST /predict    -> upload an image, get a real prediction from your
                      trained oil_spill_final.keras model

Run from the oil-spill-project root:
    .\venv311\Scripts\python.exe -m pip install fastapi uvicorn python-multipart --default-timeout=300
    .\venv311\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000

Then open dashboard/index.html in your browser (it calls http://localhost:8000).
"""

import io
import json
import os

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "oil_spill_final.keras")
METRICS_PATH = os.path.join(PROJECT_ROOT, "results", "metrics.json")
IMG_SIZE = (224, 224)
CLASS_NAMES = ["no-oil-spill", "oil-spill"]  # matches your training folder order

app = FastAPI(title="MARIS Backend")

# Allow the dashboard (opened as a local file or on a dev server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded. Backend ready.")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}


@app.get("/metrics")
def get_metrics():
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(
            status_code=404,
            detail="No metrics found yet. Run src/evaluate_model.py first.",
        )
    with open(METRICS_PATH) as f:
        return json.load(f)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    raw = await file.read()
    try:
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read that image file.")

    image = image.resize(IMG_SIZE)
    arr = np.array(image, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)  # batch of 1

    prob = float(model.predict(arr, verbose=0).flatten()[0])
    predicted_class = 1 if prob >= 0.5 else 0
    label = CLASS_NAMES[predicted_class]
    confidence = prob if predicted_class == 1 else 1 - prob

    return {
        "label": label,
        "is_oil_spill": bool(predicted_class == 1),
        "confidence": round(confidence, 4),
        "raw_oil_probability": round(prob, 4),
    }
