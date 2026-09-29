import xml.etree.ElementTree as ET

XML_PATH = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE\annotation\calibration\calibration-s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.xml"

root = ET.parse(XML_PATH).getroot()

print("Root tag:")
print(root.tag)

print("\nCalibration vectors:")
count = 0

for elem in root.iter():
    if elem.tag.endswith("calibrationVector"):
        count += 1

        line = None
        pixel = None
        sigma = None

        for child in elem:
            tag = child.tag.split("}")[-1]

            if tag == "line":
                line = child.text
            elif tag == "pixel":
                pixel = child.text
            elif tag == "sigmaNought":
                sigma = child.text

        print(f"\nVector {count}")
        print("Line:", line)
        print("Pixels:", (pixel[:100] + "...") if pixel else "None")
        print("SigmaNought:", (sigma[:100] + "...") if sigma else "None")

        if count >= 3:
            break

print("\nTotal vectors inspected:", count)
