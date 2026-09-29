import glob
import os

SAFE_DIR = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE"

files = glob.glob(os.path.join(SAFE_DIR, "annotation", "*.xml"))

print("Annotation files found:")
for f in files:
    print(" -", f)

print("\nCalibration files:")
files = glob.glob(os.path.join(SAFE_DIR, "annotation", "*.xml"))
for f in files:
    if "cal" in os.path.basename(f).lower() or "noise" in os.path.basename(f).lower():
        print(" -", f)
