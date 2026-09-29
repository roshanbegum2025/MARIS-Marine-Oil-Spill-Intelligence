import os
from PIL import Image

DATA_DIR = r"C:\Users\farzz\Downloads\oil-spill-project\data"

classes = ["no-oil-spill", "oil-spill"]

for class_name in classes:
    folder = os.path.join(DATA_DIR, "train", class_name)

    images = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    print("\n" + class_name.upper())
    print("-" * 30)

    for filename in images[:5]:
        image_path = os.path.join(folder, filename)

        try:
            image = Image.open(image_path)
            print(
                filename,
                "->",
                image.size,
                "->",
                image.mode
            )
        except Exception as e:
            print(filename, "-> ERROR:", e)

print("\nImage inspection completed successfully!")