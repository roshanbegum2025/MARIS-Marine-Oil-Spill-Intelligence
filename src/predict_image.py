import tensorflow as tf
import numpy as np
from PIL import Image

# ==============================
# 1. SETTINGS
# ==============================

MODEL_PATH = r"models\oil_spill_mobilenetv2.keras"

IMG_SIZE = (224, 224)

CLASS_NAMES = ["no-oil-spill", "oil-spill"]


# ==============================
# 2. LOAD MODEL
# ==============================

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully!")


# ==============================
# 3. GET IMAGE PATH
# ==============================

image_path = input("\nEnter image path: ")


# ==============================
# 4. LOAD AND PREPARE IMAGE
# ==============================

image = Image.open(image_path).convert("RGB")

image = image.resize(IMG_SIZE)

image_array = np.array(image)

image_array = np.expand_dims(image_array, axis=0)


# ==============================
# 5. PREDICT
# ==============================

prediction = model.predict(image_array, verbose=0)[0][0]


# ==============================
# 6. DISPLAY RESULT
# ==============================

if prediction >= 0.5:
    predicted_class = "oil-spill"
    confidence = prediction
else:
    predicted_class = "no-oil-spill"
    confidence = 1 - prediction


print("\nPrediction Result")
print("-" * 30)

print("Prediction :", predicted_class.upper())
print(f"Confidence : {confidence * 100:.2f}%")