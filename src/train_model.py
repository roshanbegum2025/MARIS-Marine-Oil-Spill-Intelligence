import tensorflow as tf
from tensorflow.keras import layers, models

# ==============================
# 1. PATHS AND SETTINGS
# ==============================

DATA_DIR = r"C:\Users\farzz\Downloads\oil-spill-project\data"

TRAIN_DIR = DATA_DIR + r"\train"
VALID_DIR = DATA_DIR + r"\valid"

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10


# ==============================
# 2. LOAD DATASET
# ==============================

train_data = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=42
)

valid_data = tf.keras.utils.image_dataset_from_directory(
    VALID_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print("\nClasses:")
print(train_data.class_names)


# ==============================
# 3. DATA AUGMENTATION
# ==============================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1)
])


# ==============================
# 4. LOAD MOBILENETV2
# ==============================

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

# Freeze pretrained layers
base_model.trainable = False


# ==============================
# 5. BUILD MODEL
# ==============================

inputs = layers.Input(shape=(224, 224, 3))

x = data_augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

x = base_model(x, training=False)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.3)(x)

outputs = layers.Dense(1, activation="sigmoid")(x)

model = models.Model(inputs, outputs)


# ==============================
# 6. COMPILE MODEL
# ==============================

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()


# ==============================
# 7. CALLBACKS
# ==============================

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True
)

checkpoint = tf.keras.callbacks.ModelCheckpoint(
    "models/oil_spill_mobilenetv2.keras",
    monitor="val_accuracy",
    save_best_only=True
)


# ==============================
# 8. TRAIN MODEL
# ==============================

print("\nStarting training...\n")

history = model.fit(
    train_data,
    validation_data=valid_data,
    epochs=EPOCHS,
    callbacks=[early_stopping, checkpoint]
)


# ==============================
# 9. SAVE FINAL MODEL
# ==============================

model.save("models/oil_spill_final.keras")

print("\nTraining completed successfully!")
print("Model saved in the models folder.")