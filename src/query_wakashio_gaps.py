import os
import requests

TOKEN = os.getenv("GFW_API_TOKEN")

if not TOKEN:
    print("ERROR: GFW_API_TOKEN not found.")
    raise SystemExit(1)

URL = "https://gateway.api.globalfishingwatch.org/v3/events"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

MIN_LAT = -20.50
MAX_LAT = -20.25
MIN_LON = 57.60
MAX_LON = 57.85

LIMIT = 1000
offset = 0

all_regional_events = []

print("Searching ALL GFW AIS gap events...")
print("Period: 2020-08-09 to 2020-08-11")
print("Region: Wakashio area")
print("---------------------------------------------")

while True:

    params = {
        "datasets[0]": "public-global-gaps-events:latest",
        "types[0]": "GAP",
        "start-date": "2020-08-09",
        "end-date": "2020-08-11",
        "limit": LIMIT,
        "offset": offset
    }

    response = requests.get(
        URL,
        headers=headers,
        params=params,
        timeout=60
    )

    print(f"\nRequest offset {offset} -> HTTP {response.status_code}")

    if not response.ok:
        print(response.text[:5000])
        raise SystemExit(1)

    data = response.json()

    events = data.get("entries", [])
    total = data.get("total", 0)

    print("Events returned:", len(events))
    print("Total events:", total)

    for event in events:

        position = event.get("position") or {}

        lat = position.get("lat")
        lon = position.get("lon")

        if lat is None or lon is None:
            continue

        if (
            MIN_LAT <= lat <= MAX_LAT
            and MIN_LON <= lon <= MAX_LON
        ):
            all_regional_events.append(event)

    offset += LIMIT

    if offset >= total or not events:
        break

print("\n=============================================")
print("FINAL RESULTS")
print("=============================================")

print("Regional AIS gaps found:", len(all_regional_events))

if not all_regional_events:

    print("\nNo GFW AIS gap events were found inside")
    print("the Wakashio candidate region in the retrieved")
    print("gap-event records.")

else:

    for i, event in enumerate(all_regional_events, 1):

        vessel = event.get("vessel") or {}
        position = event.get("position") or {}

        print(f"\nEvent {i}")
        print("--------------------------------")
        print("Event ID :", event.get("id"))
        print("Start    :", event.get("start"))
        print("End      :", event.get("end"))
        print("Latitude :", position.get("lat"))
        print("Longitude:", position.get("lon"))
        print("Vessel   :", vessel.get("name"))
        print("SSVID    :", vessel.get("ssvid"))
        print("Flag     :", vessel.get("flag"))
        print("Type     :", vessel.get("type"))

print("\nFull GFW AIS-gap search completed!")
