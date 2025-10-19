"""
Example: Multi-city flight search
複数都市周遊便の検索例

⚠️ Note: Multi-city parsing is not yet fully implemented in the current parser.
The query URL is generated correctly, but parsing the results may fail.
This is a work in progress feature.

注意: 現在のパーサーでは複数都市周遊便の解析が未実装です。
クエリURLは正しく生成されますが、結果の解析に失敗する可能性があります。
この機能は開発中です。
"""

from pprint import pprint

from fast_flights import FlightQuery, Passengers, create_query, get_flights

# Multi-city query: Tokyo → Osaka → Fukuoka → Tokyo
# 複数都市クエリ: 東京 → 大阪 → 福岡 → 東京
query = create_query(
    flights=[
        FlightQuery(
            date="2025-12-25",  # Tokyo → Osaka (東京 → 大阪)
            from_airport="HND",
            to_airport="KIX",
        ),
        FlightQuery(
            date="2025-12-27",  # Osaka → Fukuoka (大阪 → 福岡)
            from_airport="KIX",
            to_airport="FUK",
        ),
        FlightQuery(
            date="2025-12-29",  # Fukuoka → Tokyo (福岡 → 東京)
            from_airport="FUK",
            to_airport="HND",
        ),
    ],
    seat="economy",
    trip="multi-city",  # Important: Set to "multi-city"
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest",
)

print("=" * 80)
print("Multi-city Flight Search (複数都市周遊便検索)")
print("=" * 80)
print("Route: HND → KIX → FUK → HND")
print("  Leg 1: Tokyo (Haneda) → Osaka (Kansai) - 2025-12-25")
print("  Leg 2: Osaka (Kansai) → Fukuoka - 2025-12-27")
print("  Leg 3: Fukuoka → Tokyo (Haneda) - 2025-12-29")
print(f"\nQuery URL: {query.url()}\n")

print("Fetching flights...\n")

try:
    result = get_flights(query)

    print(f"✓ Found {len(result)} multi-city flight options\n")

    # Display top 3 results
    print("Top 3 cheapest options:")
    print("=" * 80)

    for i, flight in enumerate(result[:3], 1):
        print(f"\n{i}. Total Price: ¥{flight.price:,}")
        print(f"   Airlines: {', '.join(flight.airlines)}")
        print(f"   Number of segments: {len(flight.flights)}")

        # Group segments by leg
        legs = [
            ("Leg 1: Tokyo → Osaka", "HND", "KIX"),
            ("Leg 2: Osaka → Fukuoka", "KIX", "FUK"),
            ("Leg 3: Fukuoka → Tokyo", "FUK", "HND"),
        ]

        for j, segment in enumerate(flight.flights, 1):
            # Determine which leg this segment belongs to
            leg_info = "Segment"
            for leg_num, (leg_name, from_code, to_code) in enumerate(legs, 1):
                if segment.from_airport.code == from_code and segment.to_airport.code == to_code:
                    leg_info = leg_name
                    break

            print(f"\n   {leg_info}:")
            print(f"     ✈ Flight: {segment.flight_number}")
            print(f"     📍 Route: {segment.from_airport.code} → {segment.to_airport.code}")

            # Format departure date and time
            dep_date = f"{segment.departure.date[0]}-{segment.departure.date[1]:02d}-{segment.departure.date[2]:02d}"
            dep_time = ":".join(str(t).zfill(2) for t in segment.departure.time)
            print(f"     🕐 Departure: {dep_date} {dep_time}")

            # Format arrival date and time
            arr_date = f"{segment.arrival.date[0]}-{segment.arrival.date[1]:02d}-{segment.arrival.date[2]:02d}"
            arr_time = ":".join(str(t).zfill(2) for t in segment.arrival.time)
            print(f"     🕑 Arrival: {arr_date} {arr_time}")

            print(f"     ⏱ Duration: {segment.duration} min")
            print(f"     ✈️ Aircraft: {segment.plane_type}")

        print(f"\n   🌍 Total Carbon Emission: {flight.carbon.emission:,} g CO2")

    # Optionally print full details
    print("\n" + "=" * 80)
    print("Full result details (結果の詳細):")
    print("=" * 80)
    pprint(result[:1])  # Print first result in detail

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
    print("\nNote: Multi-city flights may not always be available for all routes.")
    print("Try adjusting the dates or routes if you encounter errors.")
