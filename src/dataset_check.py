import os

DATA_DIR = r"C:\Users\farzz\Downloads\oil-spill-project\data"

splits = ["train", "valid", "test"]
classes = ["no-oil-spill", "oil-spill"]

print("OIL SPILL DATASET SUMMARY")
print("=" * 40)

total = 0

for split in splits:
    print(f"\n{split.upper()}")

    split_total = 0

    for class_name in classes:
        folder = os.path.join(DATA_DIR, split, class_name)

        count = len([
            f for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        print(f"{class_name}: {count}")
        split_total += count

    print(f"Total: {split_total}")
    total += split_total

print("\n" + "=" * 40)
print("TOTAL IMAGES:", total)