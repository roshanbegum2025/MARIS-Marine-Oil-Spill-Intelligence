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

params = {
    "datasets[0]": "public-global-gaps-events:latest",
    "types[0]": "GAP",
    "start-date": "2020-08-09",
    "end-date": "2020-08-11",
    "limit": 10,
    "offset": 0
}

print("Testing GFW historical AIS-gap Events API...")
print("----------------------------------------------")

response = requests.get(
    URL,
    headers=headers,
    params=params,
    timeout=60
)

print("HTTP status:", response.status_code)

if response.ok:

    data = response.json()

    print("GFW AIS-gap API request successful!")
    print("Dataset:", data.get("metadata", {}).get("datasets"))
    print("Date range:", data.get("metadata", {}).get("dateRange"))
    print("Total events:", data.get("total", 0))
    print("Events returned:", len(data.get("entries", [])))

    for event in data.get("entries", [])[:5]:

        print("\nEvent:")
        print("  ID:", event.get("id"))
        print("  Type:", event.get("type"))
        print("  Start:", event.get("start"))
        print("  End:", event.get("end"))
        print("  Position:", event.get("position"))
        print("  Vessel:", event.get("vessel"))

else:

    print("GFW AIS-gap API request failed.")
    print(response.text[:5000])
