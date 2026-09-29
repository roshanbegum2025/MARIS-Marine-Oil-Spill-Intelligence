import xml.etree.ElementTree as ET
import os

xml_path = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE\annotation\s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

points = []

for point in root.iter():
    if point.tag.endswith("geolocationGridPoint"):
        values = {}
        for child in point:
            name = child.tag.split("}")[-1]
            values[name] = child.text

        if all(k in values for k in ["line", "pixel", "latitude", "longitude"]):
            points.append(values)

print("Total geolocation points:", len(points))

print("\nFirst 5 points:")
for p in points[:5]:
    print(
        "Line:", p["line"],
        "Pixel:", p["pixel"],
        "Lat:", p["latitude"],
        "Lon:", p["longitude"]
    )

print("\nLast 5 points:")
for p in points[-5:]:
    print(
        "Line:", p["line"],
        "Pixel:", p["pixel"],
        "Lat:", p["latitude"],
        "Lon:", p["longitude"]
    )
