"""
Example: How to fetch cheapest flight prices
"""

from fast_flights import FlightQuery, Passengers, create_query, get_flights

# Create a query with price_type="cheapest"
query = create_query(
    flights=[FlightQuery(date="2025-12-19", from_airport="MYJ", to_airport="LON")],
    seat="economy",
    trip="one-way",
    passengers=Passengers(adults=1),
    language="en-US",
    price_type="cheapest",  # This is the key parameter for getting cheapest prices
)

print("Query URL:", query.url())
print("\nFetching cheapest prices...")

try:
    flights = get_flights(query)
    print(f"\n✓ Found {len(flights)} flights")
    print(f"\nTop 5 cheapest flights:")
    for i, flight in enumerate(flights[:5], 1):
        print(f"  {i}. {flight.price:,} - {', '.join(flight.airlines)}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nNote: This example requires a working internet connection and may")
    print("fail if Google Flights changes their HTML structure.")
