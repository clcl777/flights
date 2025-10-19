"""
Analyze GetShoppingResults API request structure
"""

import urllib.parse
import json

# Request body from Chrome DevTools
request_body = "f.req=%5Bnull%2C%22%5B%5Bnull%2Cnull%2Cnull%2C%5C%22HtsiyzgHdg2IAKs2tgBG--------tbbyo21AAAAAGj0xqkG62GiA%5C%22%5D%2C%5Bnull%2Cnull%2C3%2Cnull%2C%5B%5D%2C1%2C%5B1%2C0%2C0%2C0%5D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B%5B%5B%5B%5C%22HND%5C%22%2C0%5D%5D%5D%2C%5B%5B%5B%5C%22ICN%5C%22%2C0%5D%5D%5D%2Cnull%2C0%2Cnull%2Cnull%2C%5C%222025-12-25%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C3%5D%2C%5B%5B%5B%5B%5C%22ICN%5C%22%2C0%5D%5D%5D%2C%5B%5B%5B%5C%22FUK%5C%22%2C0%5D%5D%5D%2Cnull%2C0%2Cnull%2Cnull%2C%5C%222026-01-01%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C3%5D%2C%5B%5B%5B%5B%5C%22FUK%5C%22%2C0%5D%5D%5D%2C%5B%5B%5B%5C%22HND%5C%22%2C0%5D%5D%5D%2Cnull%2C0%2Cnull%2Cnull%2C%5C%222026-02-18%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C3%5D%5D%2Cnull%2Cnull%2Cnull%2C1%5D%2C2%2C0%2C0%2C2%5D%22%5D&"

# Parse URL-encoded data
parsed = urllib.parse.parse_qs(request_body)

print("=" * 80)
print("Request Body Structure")
print("=" * 80)

if "f.req" in parsed:
    f_req = parsed["f.req"][0]
    print(f"\nf.req (URL decoded):")
    decoded = urllib.parse.unquote(f_req)
    print(decoded)

    print("\n" + "=" * 80)
    print("Attempting to parse as JSON")
    print("=" * 80)

    try:
        # Try to parse the outer array
        data = json.loads(decoded)
        print(f"\nOuter structure: {type(data)}")
        print(f"Length: {len(data)}")
        print(f"Element 0: {data[0]}")
        print(f"Element 1 type: {type(data[1])}")

        # Parse inner JSON string
        if isinstance(data[1], str):
            inner_data = json.loads(data[1])
            print(f"\nInner structure: {type(inner_data)}")
            print(f"Length: {len(inner_data)}")
            print(f"\nElement 0: {inner_data[0]}")
            print(f"Element 1: {inner_data[1]}")

            if len(inner_data) > 1 and inner_data[1]:
                query_data = inner_data[1]
                print(f"\nQuery data structure:")
                print(f"  [0]: {query_data[0]}")
                print(f"  [1]: {query_data[1]}")
                print(f"  [2]: trip type = {query_data[2]}")

                if len(query_data) > 4 and query_data[4]:
                    flights = query_data[4]
                    print(f"\nFlights array length: {len(flights)}")
                    for i, flight in enumerate(flights):
                        print(f"\nFlight {i+1}:")
                        print(f"  From: {flight[0][0][0]}")
                        print(f"  To: {flight[1][0][0]}")
                        print(f"  Date: {flight[6]}")
                        print(f"  Seat class: {flight[13]}")

    except Exception as e:
        print(f"\nError parsing JSON: {e}")
        import traceback

        traceback.print_exc()
