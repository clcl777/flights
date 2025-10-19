"""
Example: Round-trip flight search
往復便の検索例
"""

from pprint import pprint

from fast_flights import FlightQuery, Passengers, create_query, get_flights

# Round-trip query: Tokyo (HND) ⇄ Osaka (KIX)
# 往復クエリ: 東京（羽田） ⇄ 大阪（関空）
query = create_query(
    flights=[
        FlightQuery(
            date="2025-12-25",  # Outbound: December 25, 2025 (往路)
            from_airport="HND",
            to_airport="KIX",
        ),
        FlightQuery(
            date="2025-12-28",  # Return: December 28, 2025 (復路)
            from_airport="KIX",
            to_airport="HND",
        ),
    ],
    seat="economy",
    trip="round-trip",  # Important: Set to "round-trip"
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest",
)

print("=" * 80)
print("Round-trip Flight Search (往復便検索)")
print("=" * 80)
print(f"Route: HND ⇄ KIX")
print(f"Outbound: 2025-12-25 (往路)")
print(f"Return: 2025-12-28 (復路)")
print(f"Query URL: {query.url()}\n")

print("Fetching flights...\n")

try:
    result = get_flights(query)

    print(f"✓ Found {len(result)} round-trip flight options\n")

    # Display top 3 results
    print("Top 3 cheapest options:")
    print("=" * 80)

    for i, flight in enumerate(result[:3], 1):
        print(f"\n{i}. Total Price: ¥{flight.price:,}")
        print(f"   Airlines: {', '.join(flight.airlines)}")
        print(f"   Number of segments: {len(flight.flights)}")

        for j, segment in enumerate(flight.flights, 1):
            direction = "Outbound (往路)" if j <= len(flight.flights) // 2 else "Return (復路)"
            print(f"\n   Segment {j} - {direction}:")
            print(f"     ✈ Flight: {segment.flight_number}")
            print(f"     📍 Route: {segment.from_airport.code} → {segment.to_airport.code}")

            # Format departure time
            dep_time = ":".join(str(t).zfill(2) for t in segment.departure.time)
            print(f"     🕐 Departure: {dep_time}")

            # Format arrival time
            arr_time = ":".join(str(t).zfill(2) for t in segment.arrival.time)
            print(f"     🕑 Arrival: {arr_time}")

            print(f"     ⏱ Duration: {segment.duration} min")
            print(f"     ✈️ Aircraft: {segment.plane_type}")

        print(f"\n   🌍 Carbon Emission: {flight.carbon.emission:,} g CO2")

    # Optionally print full details
    print("\n" + "=" * 80)
    print("Full result details (結果の詳細):")
    print("=" * 80)
    pprint(result[:1])  # Print first result in detail

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
