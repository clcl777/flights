"""Test booking URL parsing."""

import json
from urllib.parse import parse_qs, unquote, urlparse

# The booking URL provided by the user
booking_url = "https://www.google.com/travel/flights/booking?tfs=CBwQAho_EgoyMDI1LTEyLTI1Ih8KA0hORBIKMjAyNS0xMi0yNRoDSUNOKgJPWjIDMTc3agcIARIDSE5EcgcIARIDSUNOGj8SCjIwMjYtMDEtMDEiHwoDSUNOEgoyMDI2LTAxLTAxGgNGVUsqAk9aMgMxMzRqBwgBEgNJQ05yBwgBEgNGVUsaPxIKMjAyNi0wMi0xOCIfCgNGVUsSCjIwMjYtMDItMTgaA0hORCoCSkwyAzMwMGoHCAESA0ZVS3IHCAESA0hOREABSAFwAYIBCwj___________8BmAED&tfu=CmxDalJJVVdRNVRFcGxOM1V6Y1VWQlRFZHRWWGRDUnkwdExTMHRMUzB0TFhSc2Mza3hNMEZCUVVGQlIyb3dlV3N3U0V0Q1NFVkJFZ1ZLVERNd01Cb0xDTDJDQ0JBQUdnTktVRms0SEhDenFnVT0SBggCIAIoFSIDCgEw&hl=en-US"

# Parse URL
parsed = urlparse(booking_url)
query_params = parse_qs(parsed.query)

print("=" * 80)
print("Booking URL Analysis")
print("=" * 80)

# Print TFS parameter
tfs = query_params["tfs"][0]
print(f"\nTFS parameter (raw): {tfs[:100]}...")

# Decode TFS using protobuf
from fast_flights.booking import decode_tfs_parameter

try:
    flight_query = decode_tfs_parameter(tfs)
    print("\nDecoded TFS (protobuf):")
    print(flight_query)

    print("\nFlight legs:")
    for i, leg in enumerate(flight_query.legs):
        print(f"  Leg {i + 1}:")
        print(f"    Origin: {leg.origin}")
        print(f"    Destination: {leg.destination}")
        print(f"    Date: {leg.date}")
        if leg.flights:
            flight = leg.flights[0]
            print(f"    Airline: {flight.airline}")
            print(f"    Flight number: {flight.flight_number}")
except Exception as e:
    print(f"Error decoding TFS: {e}")

# Analyze the request body from Chrome DevTools
print("\n" + "=" * 80)
print("API Request Body Analysis")
print("=" * 80)

# The actual request body from the network capture
request_body_encoded = "f.req=%5Bnull%2C%22%5B%5Bnull%2C%5C%22CjRIUWQ5TEplN3UzcUVBTEdtVXdCRy0tLS0tLS0tLXRsc3kxM0FBQUFBR2oweWswSEtCSEVBEgVKTDMwMBoLCL2CCBAAGgNKUFk4HHCzqgU%3D%5C%22%5D%2C%5Bnull%2Cnull%2C3%2Cnull%2C%5B%5D%2C1%2C%5B1%2C0%2C0%2C0%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B%5B%5B%5B%5C%22HND%5C%22%2C0%5D%5D%5D%2C%5B%5B%5B%5C%22ICN%5C%22%2C0%5D%5D%5D%2Cnull%2C0%2Cnull%2Cnull%2C%5C%222025-12-25%5C%22%2Cnull%2C%5B%5B%5C%22HND%5C%22%2C%5C%222025-12-25%5C%22%2C%5C%22ICN%5C%22%2Cnull%2C%5C%22OZ%5C%22%2C%5C%22177%5C%22%5D%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C3%5D%2C%5B%5B%5B%5B%5C%22ICN%5C%22%2C0%5D%5D%5D%2C%5B%5B%5B%5C%22FUK%5C%22%2C0%5D%5D%5D%2Cnull%2C0%2Cnull%2Cnull%2C%5C%222026-01-01%5C%22%2Cnull%2C%5B%5B%5C%22ICN%5C%22%2C%5C%222026-01-01%5C%22%2C%5C%22FUK%5C%22%2Cnull%2C%5C%22OZ%5C%22%2C%5C%22134%5C%22%5D%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C3%5D%2C%5B%5B%5B%5B%5C%22FUK%5C%22%2C0%5D%5D%5D%2C%5B%5B%5B%5C%22HND%5C%22%2C0%5D%5D%5D%2Cnull%2C0%2Cnull%2Cnull%2C%5C%222026-02-18%5C%22%2Cnull%2C%5B%5B%5C%22FUK%5C%22%2C%5C%222026-02-18%5C%22%2C%5C%22HND%5C%22%2Cnull%2C%5C%22JL%5C%22%2C%5C%22300%5C%22%5D%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C3%5D%5D%2Cnull%2Cnull%2Cnull%2C1%5D%2Cnull%2C1%2C2%5D%22%5D&"

# Parse the query string
body_params = parse_qs(request_body_encoded)
f_req = unquote(body_params["f.req"][0])

print("\nDecoded f.req parameter:")
print(f_req[:500] + "...")

# Try to parse as JSON
try:
    # The f.req contains escaped JSON, need to unescape
    # It's a list with a null first element and a JSON string second element
    outer_list = json.loads(f_req)
    print("\nOuter structure parsed:")
    print(f"  Type: {type(outer_list)}")
    print(f"  Length: {len(outer_list)}")

    if len(outer_list) > 1 and isinstance(outer_list[1], str):
        inner_json = json.loads(outer_list[1])
        print("\nInner JSON structure:")
        print(json.dumps(inner_json, indent=2)[:1000] + "...")
except Exception as e:
    print(f"Error parsing JSON: {e}")
    import traceback

    traceback.print_exc()

# Analyze the response
print("\n" + "=" * 80)
print("API Response Analysis")
print("=" * 80)

response_sample = """
[["OZ",["Asiana Airlines"],[[null,null,null,"HND","Haneda Airport","Incheon International Airport","ICN",null,[1,30],null,[4,10],160,null,null,null,[[\"NH\",\"6895\",null,\"ANA\"]],1,\"Airbus A321neo\",[true],false,[2025,12,25],[2025,12,25],[\"OZ\",\"177\",null,\"Asiana Airlines\"],null,null,1,null,null,null,null,null,108687,2]],"HND",[2025,12,25],[1,30],"ICN",[2025,12,25],[4,10],160,null,null,false,null,null,null,["ANA"],"ElFO1b",[[1760873698356439,99198714,1745724454],null,null,null,null,[[2]]],1,null,null,null,[1],[["OZ","Asiana Airlines","https://flyasiana.com/C/KR/EN/contents/disabled-passenger"]]]
"""

print("\nResponse structure (sample):")
print("This contains:")
print("  - Airline code and name")
print("  - Flight details (airport codes, times, duration)")
print("  - Aircraft type")
print("  - Flight number")
print("  - Carbon emissions")

print("\n" + "=" * 80)
print("Implementation Plan")
print("=" * 80)
print(
    """
1. Extract TFS parameter from booking URL
2. Decode TFS to get flight segments (origin, destination, date, airline, flight number)
3. Build f.req parameter with the flight details
4. Make POST request to GetBookingResults API
5. Parse response to extract:
   - Flight details (times, airports, aircraft, etc.)
   - Total price
   - Booking provider options
"""
)
