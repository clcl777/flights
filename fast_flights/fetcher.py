import json
import urllib.parse
from typing import Optional, Union, overload

from primp import Client

from .integrations import Integration
from .parser import MetaList, parse
from .querying import Query

URL = "https://www.google.com/travel/flights"
API_URL = (
    "https://www.google.com/_/FlightsFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetShoppingResults"
)


@overload
def get_flights(q: str, /, *, proxy: Optional[str] = None):
    """Get flights using a str query.

    Examples:
    - *Flights from TPE to MYJ on 2025-12-22 one way economy class*
    """


@overload
def get_flights(q: Query, /, *, proxy: Optional[str] = None):
    """Get flights using a structured query.

    Example:
    ```python
    get_flights(
        query(
            flights=[
                FlightQuery(
                    date="2025-12-22",
                    from_airport="TPE",
                    to_airport="MYJ",
                )
            ],
            seat="economy",
            trip="one-way",
            passengers=Passengers(adults=1),
            language="en-US",
            currency="",
        )
    )
    ```
    """


def get_flights(
    q: Union[Query, str],
    /,
    *,
    proxy: Optional[str] = None,
    integration: Optional[Integration] = None,
) -> MetaList:
    """Get flights.

    Args:
        q: The query.
        proxy (str, optional): Proxy.
    """
    html = fetch_flights_html(q, proxy=proxy, integration=integration)
    return parse(html)


def fetch_flights_html(
    q: Union[Query, str],
    /,
    *,
    proxy: Optional[str] = None,
    integration: Optional[Integration] = None,
) -> str:
    """Fetch flights and get the **HTML**.

    Args:
        q: The query.
        proxy (str, optional): Proxy.
    """
    if integration is None:
        # Check if this is a multi-city query with 3+ legs
        # For these queries, we need to use the API instead of HTML scraping
        if isinstance(q, Query) and q.trip == 3 and len(q.flight_data) >= 3:
            return fetch_flights_via_api(q, proxy=proxy)

        client = Client(
            impersonate="chrome_133",
            impersonate_os="macos",
            referer=True,
            proxy=proxy,
            cookie_store=True,
        )

        if isinstance(q, Query):
            params = q.params()

        else:
            params = {"q": q}

        res = client.get(URL, params=params)
        return res.text

    else:
        return integration.fetch_html(q)


def _build_api_request_body(query: Query) -> str:
    """Build GetShoppingResults API request body.

    This is used for multi-city queries with 3+ legs where the initial HTML
    doesn't contain flight data and requires a dynamic API call.
    """
    # Build the query data structure similar to the protobuf format
    # Structure: [session_info, query_data, 2, 0, 0, 2]

    # Build flights array
    flights_data = []
    for flight_data in query.flight_data:
        flight_entry = [
            [[[flight_data.from_airport.airport, 0]]],  # Origin
            [[[flight_data.to_airport.airport, 0]]],  # Destination
            None,
            0,
            None,
            None,
            flight_data.date,  # Date
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            query.seat,  # Cabin class (1=economy, 2=premium_economy, 3=business, 4=first)
        ]
        flights_data.append(flight_entry)

    # Trip type is already an integer (1=one-way, 2=round-trip, 3=multi-city)
    trip_type = query.trip

    # Count passengers by type
    # Passenger enum: ADULT=1, CHILD=2, INFANT_IN_SEAT=3, INFANT_ON_LAP=4
    adults = sum(1 for p in query.passengers if p == 1)
    children = sum(1 for p in query.passengers if p == 2)
    infants_in_seat = sum(1 for p in query.passengers if p == 3)
    infants_on_lap = sum(1 for p in query.passengers if p == 4)

    passengers_data = [adults, children, infants_in_seat, infants_on_lap]

    # Build query structure
    query_data = [
        None,
        None,
        trip_type,
        None,
        [],
        1,
        passengers_data,
        None,
        None,
        None,
        None,
        None,
        None,
        flights_data,
        None,
        None,
        None,
        1,
    ]

    # Build outer structure
    # [session_info, query_data, 2, 0, 0, 2]
    inner_data = [
        [None, None, None, ""],  # Session info placeholder
        query_data,
        2,
        0,
        0,
        2,
    ]

    # Convert to JSON string
    inner_json = json.dumps(inner_data, separators=(",", ":"))

    # Wrap in outer array
    outer_data = [None, inner_json]
    outer_json = json.dumps(outer_data, separators=(",", ":"))

    # URL encode for POST body
    body = f"f.req={urllib.parse.quote(outer_json)}&"

    return body


def fetch_flights_via_api(
    query: Query,
    /,
    *,
    proxy: Optional[str] = None,
) -> str:
    """Fetch flights using the GetShoppingResults API.

    This is used for multi-city queries with 3+ legs where the initial HTML
    doesn't contain flight data.

    Args:
        query: The query object.
        proxy: Optional proxy string.

    Returns:
        HTML-like structure containing the flight data.
    """
    client = Client(
        impersonate="chrome_133",
        impersonate_os="macos",
        referer=True,
        proxy=proxy,
        cookie_store=True,
    )

    # Build request body
    body = _build_api_request_body(query)

    # Build query parameters
    params = {
        "f.sid": "1",  # Session ID placeholder
        "bl": "boq_travel-frontend-flights-ui_20251014.06_p0",
        "hl": query.language,
        "soc-app": "162",
        "soc-platform": "1",
        "soc-device": "1",
        "_reqid": "1",
        "rt": "c",
    }

    # Build headers
    headers = {
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "x-same-domain": "1",
        "x-goog-ext-259736195-jspb": json.dumps(
            [
                query.language,
                "JP",  # Location - TODO: make this configurable
                query.currency or "JPY",
                1,
                None,
                [-540],  # Timezone offset - TODO: make this dynamic
                None,
                None,
                7,
                [],
            ],
            separators=(",", ":"),
        ),
    }

    # Make POST request
    # Use content instead of data to pass raw body string
    res = client.post(API_URL, params=params, content=body.encode("utf-8"), headers=headers)

    # Parse response
    # Response format:
    # Line 1: )]}' (XSS protection)
    # Line 2: empty
    # Line 3: data length\nJSON data

    response_text = res.text

    # Remove XSS protection prefix
    if response_text.startswith(")]}'"):
        response_text = response_text[4:]

    # Skip empty line
    lines = response_text.split("\n", 2)
    if len(lines) < 3:
        raise ValueError("Invalid API response format")

    # Line 2 contains: "33068\n[["wrb.fr",..."
    # We need to skip the number and extract just the JSON
    data_line = lines[2]

    # Find where JSON starts (first '[' character)
    json_start = data_line.find("[")
    if json_start == -1:
        raise ValueError("No JSON data found in response")

    json_data = data_line[json_start:]

    # Parse outer JSON: [["wrb.fr", null, "<escaped_json_string>"]]
    # Note: Response contains multiple JSON arrays separated by newlines
    # We only need the first one
    decoder = json.JSONDecoder()
    outer_array, _ = decoder.raw_decode(json_data)

    if not outer_array or len(outer_array) < 1:
        raise ValueError("Unexpected API response structure")

    # Extract inner JSON string
    inner_json_str = outer_array[0][2]

    # Parse inner JSON to get flight data
    # This will be in a similar format to the HTML script data
    inner_data = json.loads(inner_json_str)

    # Convert API response to HTML-like format for the parser
    # The parser expects a script tag with data: prefix
    html_template = f"""<!DOCTYPE html>
<html>
<head></head>
<body>
<script class="ds:1">
AF_initDataCallback({{key: 'ds:1', hash: '1', data:{json.dumps(inner_data)}, sideChannel: {{}}}});
</script>
</body>
</html>"""

    return html_template
