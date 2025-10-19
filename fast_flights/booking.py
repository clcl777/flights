"""
Booking URL parser and flight information retriever.

This module provides functionality to extract flight information from
Google Flights booking URLs by calling the GetBookingResults API.
"""

import json
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse

import primp  # type: ignore


@dataclass
class BookingFlight:
    """Single flight segment in a booking."""

    airline_code: str
    airline_name: str
    flight_number: str  # Format: "AA123" (full flight code)
    from_airport_code: str
    from_airport_name: str
    to_airport_code: str
    to_airport_name: str
    departure_time: str  # "HH:MM" format
    departure_date: str  # "YYYY-MM-DD" format
    arrival_time: str  # "HH:MM" format
    arrival_date: str  # "YYYY-MM-DD" format
    duration: int  # minutes
    plane_type: str
    carbon_emissions: Optional[int]  # grams of CO2


@dataclass
class BookingProvider:
    """Booking provider option."""

    name: str
    price: int  # price in minor units (e.g., yen)
    currency: str
    url: Optional[str] = None


@dataclass
class BookingInfo:
    """Flight booking information."""

    flights: list[BookingFlight]
    total_price: Optional[int]  # Price in minor units (e.g., yen)
    currency: Optional[str]
    booking_providers: list[BookingProvider]


def get_booking_info(
    booking_url: str,
    segments: list[dict] | None = None,
) -> BookingInfo:
    """
    Extract flight information from a Google Flights booking URL.

    Args:
        booking_url: Full Google Flights booking URL containing tfs parameter
        segments: Optional list of flight segment dicts. If provided, these will be used
                 instead of attempting to decode from tfs parameter. Each segment should have:
                 - from: Origin airport code (e.g., "HND")
                 - to: Destination airport code (e.g., "ICN")
                 - date: Flight date in YYYY-MM-DD format (e.g., "2025-12-25")
                 - airline: Airline code (e.g., "OZ") - optional but recommended
                 - flight_number: Flight number (e.g., "177") - optional but recommended

    Returns:
        BookingInfo object containing flight details and pricing

    Example:
        >>> url = "https://www.google.com/travel/flights/booking?tfs=CBw..."
        >>> # Option 1: Automatic (may not work reliably)
        >>> info = get_booking_info(url)
        >>>
        >>> # Option 2: Explicit segments (recommended)
        >>> segments = [
        ...     {"from": "HND", "to": "ICN", "date": "2025-12-25", "airline": "OZ", "flight_number": "177"},
        ...     {"from": "ICN", "to": "FUK", "date": "2026-01-01", "airline": "OZ", "flight_number": "134"},
        ... ]
        >>> info = get_booking_info(url, segments=segments)
        >>> print(f"Total: {info.currency} {info.total_price}")
        >>> for flight in info.flights:
        ...     print(f"{flight.airline_name} {flight.flight_number}: "
        ...           f"{flight.from_airport_code} -> {flight.to_airport_code}")
    """
    import base64

    # Parse URL
    parsed = urlparse(booking_url)
    query_params = parse_qs(parsed.query)

    # Extract parameters
    hl = query_params.get("hl", ["en-US"])[0]

    # Get flight segments
    if segments is None:
        # Try to decode from tfs parameter
        if "tfs" not in query_params:
            raise ValueError("No 'tfs' parameter found in booking URL and no segments provided")

        tfs = query_params["tfs"][0]

        # Decode tfs to extract flight segments
        # The tfs parameter is a base64-encoded protobuf containing flight details
        segments = _decode_tfs_to_segments(tfs)

        if not segments:
            raise ValueError(
                "Failed to decode segments from tfs parameter. "
                "Please provide segments explicitly using the 'segments' argument.\n"
                "Example: segments=[{'from': 'HND', 'to': 'ICN', 'date': '2025-12-25', "
                "'airline': 'OZ', 'flight_number': '177'}]"
            )

    # Build the API request body
    request_data = _build_booking_request(segments, hl)

    # Make API request
    api_url = "https://www.google.com/_/FlightsFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetBookingResults"

    # Generate f.sid parameter (session ID)
    import random
    import time

    sid = -int(time.time() * 1000000) % (10**18)

    # Prepare headers (based on observed request)
    headers = {
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "referer": booking_url,
        "x-same-domain": "1",
        "x-goog-ext-259736195-jspb": '["en-US","JP","JPY",1,null,[-540],null,null,7,[]]',
    }

    # Prepare query parameters
    params = {
        "f.sid": str(sid),
        "bl": "boq_travel-frontend-flights-ui_20251014.06_p0",
        "hl": hl,
        "soc-app": "162",
        "soc-platform": "1",
        "soc-device": "1",
        "_reqid": str(random.randint(10000, 999999)),
        "rt": "c",
    }

    # Construct full URL with query parameters
    full_url = f"{api_url}?{urlencode(params)}"

    # Make request
    client = primp.Client(impersonate="chrome_131")
    response = client.post(
        full_url,
        headers=headers,
        data={"f.req": request_data},
        timeout=30,
    )

    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text[:200]}")

    # Parse response
    booking_info = _parse_booking_response(response.text)

    return booking_info


def _decode_tfs_to_segments(tfs: str) -> list[dict]:
    """
    Decode the tfs parameter to extract flight segments.

    The tfs is a base64-encoded protobuf. We'll parse it manually
    to extract the relevant information.
    """
    import base64
    import re

    # Add padding if necessary
    missing_padding = len(tfs) % 4
    if missing_padding:
        tfs += "=" * (4 - missing_padding)

    # Decode base64
    try:
        decoded_bytes = base64.b64decode(tfs)
    except Exception as e:
        raise ValueError(f"Failed to decode tfs parameter: {e}")

    # Convert to string (protobuf is partially text-readable)
    decoded_str = decoded_bytes.decode("utf-8", errors="ignore")

    # Extract flight segments using regex patterns
    # Pattern for date: YYYY-MM-DD
    dates = re.findall(r"(\d{4}-\d{2}-\d{2})", decoded_str)

    # Pattern for airport codes (3 uppercase letters)
    airports = re.findall(r"\b([A-Z]{3})\b", decoded_str)

    # Pattern for airline codes (2 uppercase letters/digits)
    airlines = re.findall(r"\b([A-Z0-9]{2})\b", decoded_str)

    # Pattern for flight numbers (2-4 digits)
    flight_numbers = re.findall(r"\b(\d{2,4})\b", decoded_str)

    # Build segments from extracted data
    # This is a simplified approach - in reality, we'd need proper protobuf parsing
    segments = []

    # Assuming segments come in triplets: origin, destination for each leg
    i = 0
    date_idx = 0
    airline_idx = 0
    flight_num_idx = 0

    while i < len(airports) - 1 and date_idx < len(dates):
        segment = {
            "from": airports[i],
            "to": airports[i + 1],
            "date": dates[date_idx],
        }

        # Try to find matching airline and flight number
        if airline_idx < len(airlines) and flight_num_idx < len(flight_numbers):
            segment["airline"] = airlines[airline_idx]
            segment["flight_number"] = flight_numbers[flight_num_idx]
            airline_idx += 1
            flight_num_idx += 1

        segments.append(segment)
        i += 1
        date_idx += 1

    return segments


def _build_booking_request(segments: list[dict], language: str) -> str:
    """
    Build the f.req parameter for the GetBookingResults API.

    Based on observed network requests from Chrome DevTools.
    """
    import json

    # Build segments array matching the observed structure
    segments_json = []
    for seg in segments:
        segment = [
            [[[seg["from"], 0]]],
            [[[seg["to"], 0]]],
            None,
            0,
            None,
            None,
            seg["date"],
            None,
        ]

        # Add flight details if available
        if "airline" in seg and "flight_number" in seg:
            segment.append(
                [
                    [
                        seg["from"],
                        seg["date"],
                        seg["to"],
                        None,
                        seg["airline"],
                        seg["flight_number"],
                    ]
                ]
            )
        else:
            segment.append(None)

        # Add remaining fields
        segment.extend([None, None, None, None, None, 3])
        segments_json.append(segment)

    # Construct full request structure
    inner_structure = [
        None,
        [
            None,
            None,
            3,
            None,
            [],
            1,
            [1, 0, 0, 0],
            None,
            None,
            None,
            None,
            None,
            None,
            segments_json,
            None,
            None,
            None,
            1,
        ],
        None,
        1,
        2,
    ]

    # The f.req parameter is a list with null first element and JSON string second element
    outer_structure = [None, json.dumps(inner_structure)]

    return json.dumps(outer_structure)


def _parse_booking_response(response_text: str) -> BookingInfo:
    """
    Parse the API response to extract booking information.

    The response format: )]}'\\n<length>\\n<json>\\n<length>\\n<json>...
    First JSON contains flight details, second contains booking providers.
    """
    import json

    # Remove the safety prefix
    if response_text.startswith(")]}'"):
        response_text = response_text[4:].strip()

    # Split by lines
    lines = response_text.split("\n")

    flights = []
    total_price = None
    currency = None
    booking_providers = []

    # Parse each JSON line (skip length indicators)
    for line in lines:
        if not line.strip() or line.strip().isdigit():
            continue

        try:
            data = json.loads(line)

            # Response format: [[" wrb.fr", null, "JSON_STRING"]]
            if not isinstance(data, list) or len(data) < 1:
                continue

            if isinstance(data[0], list) and len(data[0]) >= 3:
                # data[0][0] = "wrb.fr"
                # data[0][1] = null
                # data[0][2] = escaped JSON string
                if isinstance(data[0][2], str):
                    try:
                        inner_data = json.loads(data[0][2])

                        if isinstance(inner_data, list) and len(inner_data) >= 2:
                            flight_data_section = inner_data[1]

                            # Check if this is flight data or booking provider data
                            if isinstance(flight_data_section, list) and len(flight_data_section) > 0:
                                first_item = flight_data_section[0]

                                # Booking provider data: [[provider1, provider2, ...], ...]
                                if isinstance(first_item, list) and len(first_item) > 0:
                                    if isinstance(first_item[0], list) and len(first_item[0]) > 7:
                                        # This is booking provider data
                                        for provider_data in first_item:
                                            if not isinstance(provider_data, list) or len(provider_data) < 8:
                                                continue

                                            # Extract provider name from provider_data[1][0][1]
                                            provider_name = ""
                                            if (
                                                isinstance(provider_data[1], list)
                                                and len(provider_data[1]) > 0
                                                and isinstance(provider_data[1][0], list)
                                                and len(provider_data[1][0]) >= 2
                                            ):
                                                provider_name = provider_data[1][0][1]

                                            # Extract price from provider_data[7][0][1]
                                            price_value = None
                                            if (
                                                isinstance(provider_data[7], list)
                                                and len(provider_data[7]) > 0
                                                and isinstance(provider_data[7][0], list)
                                                and len(provider_data[7][0]) >= 2
                                            ):
                                                price_value = provider_data[7][0][1]

                                            # Currency is typically in the request headers (JPY for Japan)
                                            # We can extract it from the URL or use a default
                                            price_currency = "JPY"  # Default, could be extracted from request

                                            if provider_name and price_value:
                                                provider = BookingProvider(
                                                    name=provider_name,
                                                    price=price_value,
                                                    currency=price_currency,
                                                )
                                                booking_providers.append(provider)

                                                # Set total price to the first (cheapest) provider
                                                if total_price is None:
                                                    total_price = price_value
                                                    currency = price_currency

                                # Flight data: ["OZ", ["Asiana"], [[flight_details]]]
                                elif isinstance(first_item, str):
                                    # Extract flights from flight_data_section[5]
                                    if len(flight_data_section) > 5 and isinstance(flight_data_section[5], list):
                                        flights_array = flight_data_section[5]

                                        for flight_group in flights_array:
                                            if not isinstance(flight_group, list) or len(flight_group) < 3:
                                                continue

                                            airline_code = flight_group[0]
                                            airline_name = (
                                                flight_group[1][0] if isinstance(flight_group[1], list) else ""
                                            )
                                            flight_details = flight_group[2]

                                            if not isinstance(flight_details, list):
                                                continue

                                            # Parse each segment
                                            for detail in flight_details:
                                                if not isinstance(detail, list) or len(detail) < 32:
                                                    continue

                                                flight = BookingFlight(
                                                    airline_code=airline_code,
                                                    airline_name=airline_name,
                                                    flight_number=(
                                                        f"{detail[22][0]}{detail[22][1]}" if detail[22] else ""
                                                    ),
                                                    from_airport_code=detail[3] or "",
                                                    from_airport_name=detail[4] or "",
                                                    to_airport_code=detail[6] or "",
                                                    to_airport_name=detail[5] or "",
                                                    departure_time=(
                                                        f"{detail[8][0]:02d}:{detail[8][1]:02d}" if detail[8] else ""
                                                    ),
                                                    departure_date=(
                                                        f"{detail[20][0]}-{detail[20][1]:02d}-{detail[20][2]:02d}"
                                                        if detail[20]
                                                        else ""
                                                    ),
                                                    arrival_time=(
                                                        f"{detail[10][0]:02d}:{detail[10][1]:02d}" if detail[10] else ""
                                                    ),
                                                    arrival_date=(
                                                        f"{detail[21][0]}-{detail[21][1]:02d}-{detail[21][2]:02d}"
                                                        if detail[21]
                                                        else ""
                                                    ),
                                                    duration=detail[11] or 0,
                                                    plane_type=detail[17] or "",
                                                    carbon_emissions=detail[31] if len(detail) > 31 else None,
                                                )
                                                flights.append(flight)

                    except json.JSONDecodeError:
                        pass

        except (json.JSONDecodeError, IndexError, TypeError):
            continue

    return BookingInfo(
        flights=flights,
        total_price=total_price,
        currency=currency,
        booking_providers=booking_providers,
    )
