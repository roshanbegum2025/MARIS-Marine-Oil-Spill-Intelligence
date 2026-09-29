import os
import requests

TOKEN = os.getenv("GFW_API_TOKEN")

if not TOKEN:
    print("ERROR: GFW_API_TOKEN not found.")
    raise SystemExit(1)

URL = "https://gateway.api.globalfishingwatch.org/v3/vessels/search"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

params = {
    "query": "WAKASHIO",
    "datasets[0]": "public-global-vessel-identity:latest"
}

print("Testing Global Fishing Watch Vessel API...")
print("--------------------------------------------")

response = requests.get(
    URL,
    headers=headers,
    params=params,
    timeout=30
)

print("HTTP status:", response.status_code)

if response.ok:

    data = response.json()

    print("GFW API authentication successful!")
    print("Response received successfully.")
    print("Total matches:", data.get("total", 0))

    entries = data.get("entries", [])

    for vessel in entries[:5]:
        print("\nVessel:")
        print(vessel)

else:

    print("GFW API request failed.")
    print(response.text[:3000])
