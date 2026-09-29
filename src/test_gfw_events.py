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
    "start-date": "2020-08-09",
    "end-date": "2020-08-11",
    "include": "VESSEL"
}

print("Testing GFW historical Events API...")
print("-------------------------------------")

response = requests.get(
    URL,
    headers=headers,
    params=params,
    timeout=60
)

print("HTTP status:", response.status_code)

if response.ok:
    data = response.json()

    print("Events API request successful!")
    print("Response keys:", list(data.keys()))

    if isinstance(data, dict):
        print("Response preview:")
        print(str(data)[:5000])
    else:
        print("Response preview:")
        print(str(data)[:5000])

else:
    print("Events API request failed.")
    print("Response:")
    print(response.text[:5000])
