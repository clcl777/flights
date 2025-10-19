"""
Debug API response
"""

from fast_flights import create_query, FlightQuery, Passengers
from fast_flights.fetcher import _build_api_request_body
from primp import Client
import json

query = create_query(
    flights=[
        FlightQuery(date="2025-12-25", from_airport="HND", to_airport="ICN"),
        FlightQuery(date="2026-01-01", from_airport="ICN", to_airport="FUK"),
        FlightQuery(date="2026-02-18", from_airport="FUK", to_airport="HND"),
    ],
    seat="economy",
    trip="multi-city",
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest",
)

client = Client(
    impersonate="chrome_133",
    impersonate_os="macos",
    referer=True,
    cookie_store=True,
)

body = _build_api_request_body(query)

params = {
    "f.sid": "1",
    "bl": "boq_travel-frontend-flights-ui_20251014.06_p0",
    "hl": query.language,
    "soc-app": "162",
    "soc-platform": "1",
    "soc-device": "1",
    "_reqid": "1",
    "rt": "c",
}

headers = {
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "x-same-domain": "1",
    "x-goog-ext-259736195-jspb": json.dumps(
        [
            query.language,
            "JP",
            query.currency or "JPY",
            1,
            None,
            [-540],
            None,
            None,
            7,
            [],
        ],
        separators=(",", ":"),
    ),
}

API_URL = (
    "https://www.google.com/_/FlightsFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetShoppingResults"
)

res = client.post(API_URL, params=params, content=body.encode("utf-8"), headers=headers)

print("Response status:", res.status_code)
print("\nResponse length:", len(res.text))

# Save to file
with open("api_response.txt", "w") as f:
    f.write(res.text)
print("\n✓ Saved to api_response.txt")

# Show first 1000 characters
print("\nFirst 1000 characters:")
print(res.text[:1000])
