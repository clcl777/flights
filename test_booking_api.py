#!/usr/bin/env python3
"""Test booking URL API implementation."""

from fast_flights import get_booking_info

# The booking URL provided by the user
booking_url = "https://www.google.com/travel/flights/booking?tfs=CBwQAho_EgoyMDI1LTEyLTI1Ih8KA0hORBIKMjAyNS0xMi0yNRoDSUNOKgJPWjIDMTc3agcIARIDSE5EcgcIARIDSUNOGj8SCjIwMjYtMDEtMDEiHwoDSUNOEgoyMDI2LTAxLTAxGgNGVUsqAk9aMgMxMzRqBwgBEgNJQ05yBwgBEgNGVUsaPxIKMjAyNi0wMi0xOCIfCgNGVUsSCjIwMjYtMDItMTgaA0hORCoCSkwyAzMwMGoHCAESA0ZVS3IHCAESA0hOREABSAFwAYIBCwj___________8BmAED&tfu=CmxDalJJVVdRNVRFcGxOM1V6Y1VWQlRFZHRWWGRDUnkwdExTMHRMUzB0TFhSc2Mza3hNMEZCUVVGQlIyb3dlV3N3U0V0Q1NFVkJFZ1ZLVERNd01Cb0xDTDJDQ0JBQUdnTktVRms0SEhDenFnVT0SBggCIAIoFSIDCgEw&hl=en-US"

# Define flight segments explicitly
# This is the recommended approach as tfs decoding may not be reliable
segments = [
    {
        "from": "HND",
        "to": "ICN",
        "date": "2025-12-25",
        "airline": "OZ",
        "flight_number": "177",
    },
    {
        "from": "ICN",
        "to": "FUK",
        "date": "2026-01-01",
        "airline": "OZ",
        "flight_number": "134",
    },
    {
        "from": "FUK",
        "to": "HND",
        "date": "2026-02-18",
        "airline": "JL",
        "flight_number": "300",
    },
]

print("=" * 80)
print("Testing Booking URL API")
print("=" * 80)
print(f"\nBooking URL: {booking_url[:100]}...")
print(f"\nFlight Segments:")
for i, seg in enumerate(segments, 1):
    airline_info = f"{seg.get('airline', '?')} {seg.get('flight_number', '?')}"
    print(f"  {i}. {seg['from']} → {seg['to']} on {seg['date']} ({airline_info})")

try:
    print("\nFetching booking information...")
    info = get_booking_info(booking_url, segments=segments)

    print("\n" + "=" * 80)
    print("Booking Information")
    print("=" * 80)

    if info.total_price is not None:
        print(f"\nTotal Price: {info.currency} {info.total_price:,}")
    else:
        print(f"\nTotal Price: Not available")

    print(f"\nFlights ({len(info.flights)} segments):")
    print("-" * 80)

    for i, flight in enumerate(info.flights, 1):
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

    print(f"\n" + "=" * 80)
    print(f"Booking Providers ({len(info.booking_providers)} options):")
    print("-" * 80)

    for provider in info.booking_providers:
        print(f"  {provider.name}: {provider.currency} {provider.price:,}")

    print("\n" + "=" * 80)
    print("✓ Test completed successfully!")
    print("=" * 80)

except Exception as e:
    print("\n" + "=" * 80)
    print("✗ Test failed!")
    print("=" * 80)
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
