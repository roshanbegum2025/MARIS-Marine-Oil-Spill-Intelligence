import xml.etree.ElementTree as ET

XML_PATH = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE\annotation\calibration\noise-s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.xml"

root = ET.parse(XML_PATH).getroot()

print("Root tag:")
print(root.tag)

print("\nImportant XML elements:")
count = 0

for elem in root.iter():
    tag = elem.tag.split("}")[-1]

    if tag in [
        "noiseRangeVector",
        "noiseAzimuthVector",
        "line",
        "pixel",
        "noiseRangeLut",
        "noiseAzimuthLut"
    ]:
        text = (elem.text or "").strip()

        if text:
            print(f"\nTag: {tag}")
            print("Value:", text[:300])

        count += 1

        if count >= 12:
            break

print("\nInspection completed.")
