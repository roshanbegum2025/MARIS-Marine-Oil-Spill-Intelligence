import os

SAFE_DIR = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE"

print("Calibration / noise related files:")
print("-" * 50)

found = False

for root, dirs, files in os.walk(SAFE_DIR):
    for filename in files:
        name = filename.lower()
        if "calibration" in name or "noise" in name:
            print(os.path.join(root, filename))
            found = True

if not found:
    print("No files with 'calibration' or 'noise' in the filename were found.")

print("\nSearch completed.")
