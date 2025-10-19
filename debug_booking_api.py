"""Debug booking URL API implementation."""

from fast_flights.booking import _decode_tfs_to_segments

# The booking URL provided by the user
booking_url = "https://www.google.com/travel/flights/booking?tfs=CBwQAho_EgoyMDI1LTEyLTI1Ih8KA0hORBIKMjAyNS0xMi0yNRoDSUNOKgJPWjIDMTc3agcIARIDSE5EcgcIARIDSUNOGj8SCjIwMjYtMDEtMDEiHwoDSUNOEgoyMDI2LTAxLTAxGgNGVUsqAk9aMgMxMzRqBwgBEgNJQ05yBwgBEgNGVUsaPxIKMjAyNi0wMi0xOCIfCgNGVUsSCjIwMjYtMDItMTgaA0hORCoCSkwyAzMwMGoHCAESA0ZVS3IHCAESA0hOREABSAFwAYIBCwj___________8BmAED&tfu=CmxDalJJVVdRNVRFcGxOM1V6Y1VWQlRFZHRWWGRDUnkwdExTMHRMUzB0TFhSc2Mza3hNMEZCUVVGQlIyb3dlV3N3U0V0Q1NFVkJFZ1ZLVERNd01Cb0xDTDJDQ0JBQUdnTktVRms0SEhDenFnVT0SBggCIAIoFSIDCgEw&hl=en-US"

tfs = "CBwQAho_EgoyMDI1LTEyLTI1Ih8KA0hORBIKMjAyNS0xMi0yNRoDSUNOKgJPWjIDMTc3agcIARIDSE5EcgcIARIDSUNOGj8SCjIwMjYtMDEtMDEiHwoDSUNOEgoyMDI2LTAxLTAxGgNGVUsqAk9aMgMxMzRqBwgBEgNJQ05yBwgBEgNGVUsaPxIKMjAyNi0wMi0xOCIfCgNGVUsSCjIwMjYtMDItMTgaA0hORCoCSkwyAzMwMGoHCAESA0ZVS3IHCAESA0hOREABSAFwAYIBCwj___________8BmAED"

print("=" * 80)
print("Debugging TFS Parameter Decoding")
print("=" * 80)

try:
    segments = _decode_tfs_to_segments(tfs)

    print(f"\nExtracted {len(segments)} segments:")
    for i, seg in enumerate(segments, 1):
        print(f"\nSegment {i}:")
        print(f"  From: {seg.get('from')}")
        print(f"  To: {seg.get('to')}")
        print(f"  Date: {seg.get('date')}")
        print(f"  Airline: {seg.get('airline', 'N/A')}")
        print(f"  Flight Number: {seg.get('flight_number', 'N/A')}")

    # Now test the full API call
    print("\n" + "=" * 80)
    print("Testing Full API Call")
    print("=" * 80)

    from fast_flights import get_booking_info

    info = get_booking_info(booking_url)

    print(f"\nFlights found: {len(info.flights)}")
    print(f"Total price: {info.total_price}")
    print(f"Currency: {info.currency}")
    print(f"Booking providers: {len(info.booking_providers)}")

    if info.flights:
        print("\nFirst flight details:")
        flight = info.flights[0]
        print(f"  Airline: {flight.airline_name} ({flight.airline_code})")
        print(f"  Flight Number: {flight.flight_number}")
        print(f"  Route: {flight.from_airport_code} → {flight.to_airport_code}")

    if info.booking_providers:
        print("\nBooking providers:")
        for provider in info.booking_providers:
            print(f"  {provider.name}: {provider.currency} {provider.price}")

except Exception as e:
    print(f"\nError: {e}")
    import traceback

    traceback.print_exc()
