"""
Example: Display flight numbers for each segment
"""

from fast_flights import FlightQuery, Passengers, create_query, get_flights

# Create a query for domestic flights in Japan
query = create_query(
    flights=[FlightQuery(date="2025-12-19", from_airport="HND", to_airport="KIX")],
    seat="economy",
    trip="one-way",
    passengers=Passengers(adults=1),
    language="en-US",
)

print("Fetching flights with flight numbers...\n")

try:
    flights = get_flights(query)
    print(f"✓ Found {len(flights)} flights\n")

    print("Top 5 flights:")
    print("=" * 80)

    for i, flight in enumerate(flights[:5], 1):
        print(f"\n{i}. {', '.join(flight.airlines)} - ¥{flight.price:,}")

        for j, segment in enumerate(flight.flights, 1):
            print(f"   Segment {j}:")
            print(f"     ✈ Flight Number: {segment.flight_number}")
            print(f"     📍 Route: {segment.from_airport.code} → {segment.to_airport.code}")
            print(f"     🕐 Departure: {':'.join(map(str, segment.departure.time))}")
            print(f"     ✈️ Aircraft: {segment.plane_type}")
            print(f"     ⏱ Duration: {segment.duration} min")

except Exception as e:
    print(f"✗ Error: {e}")
    print("\nNote: This example requires a working internet connection.")
