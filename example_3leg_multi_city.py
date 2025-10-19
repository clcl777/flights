"""
Test 3-leg multi-city with new API implementation
HND → ICN → FUK → HND
"""
from pprint import pprint

from fast_flights import create_query, FlightQuery, Passengers, get_flights

print("=" * 80)
print("Testing 3-leg multi-city with GetShoppingResults API")
print("=" * 80)

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

print(f"\nQuery URL: {query.url()}")
print(f"Trip type: {query.trip}")
print(f"Number of legs: {len(query.flight_data)}")

print("\nFetching flights...")

try:
    flights = get_flights(query)
    
    if flights:
        print(f"\n✓ Success! Found {len(flights)} flight options")
        
        print("\nTop 3 results:\n" + "=" * 80)
        for i, flight in enumerate(flights[:3]):
            print(f"\n{i+1}. Total Price: ¥{flight.price:,}")
            print(f"   Airlines: {', '.join(flight.airlines)}")
            print(f"   Segments: {len(flight.flights)}")
            
            for j, segment in enumerate(flight.flights):
                print(f"\n   Leg {j+1}:")
                print(f"     ✈ Flight: {segment.flight_number}")
                print(f"     📍 Route: {segment.from_airport.code} → {segment.to_airport.code}")
                print(f"     🕐 Departure: {':'.join(map(str, segment.departure.time))}")
                print(f"     🕑 Arrival: {':'.join(map(str, segment.arrival.time))}")
                print(f"     ⏱ Duration: {segment.duration} min")
                print(f"     ✈️ Aircraft: {segment.plane_type}")
        
        print("\n" + "=" * 80)
        print("Full metadata:")
        print(f"  Airlines: {flights.metadata.airlines}")
        print(f"  Alliances: {flights.metadata.alliances}")
    else:
        print("✗ No flights found")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

