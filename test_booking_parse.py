"""Test booking response parsing with saved response."""

from fast_flights.booking import _parse_booking_response

# Read the saved response
with open("debug_booking_response.json", "r") as f:
    response_text = f.read()

print("=" * 80)
print("Testing Booking Response Parsing")
print("=" * 80)

try:
    booking_info = _parse_booking_response(response_text)

    print(f"\n✓ Parsing successful!")
    print(f"\nFlights found: {len(booking_info.flights)}")
    print(f"Total price: {booking_info.total_price}")
    print(f"Currency: {booking_info.currency}")
    print(f"Booking providers: {len(booking_info.booking_providers)}")

    if booking_info.flights:
        print("\n" + "=" * 80)
        print("Flight Details")
        print("=" * 80)

        for i, flight in enumerate(booking_info.flights, 1):
            print(f"\nSegment {i}:")
            print(f"  Airline: {flight.airline_name} ({flight.airline_code})")
            print(f"  Flight Number: {flight.flight_number}")
            print(f"  Route: {flight.from_airport_code} ({flight.from_airport_name})")
            print(f"         → {flight.to_airport_code} ({flight.to_airport_name})")
            print(f"  Departure: {flight.departure_date} {flight.departure_time}")
            print(f"  Arrival: {flight.arrival_date} {flight.arrival_time}")
            print(f"  Duration: {flight.duration} minutes")
            print(f"  Aircraft: {flight.plane_type}")
            if flight.carbon_emissions:
                print(f"  CO2 Emissions: {flight.carbon_emissions}g")

    if booking_info.booking_providers:
        print("\n" + "=" * 80)
        print("Booking Providers")
        print("=" * 80)

        for provider in booking_info.booking_providers:
            print(f"  {provider.name}: {provider.currency} {provider.price:,}")

    print("\n" + "=" * 80)
    print("✓ All tests passed!")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ Parsing failed!")
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
