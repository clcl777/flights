from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime as Datetime
from typing import Literal, Optional, Union

from .pb.flights_pb2 import Airport, FlightData, Info, Passenger, Seat, SortPreference, SortType, TfuData, Trip
from .types import Currency, Language, PriceType, SeatType, TripType


@dataclass
class Query:
    """A query containing `?tfs` data."""

    flight_data: list[FlightData]
    seat: Seat
    trip: Trip
    passengers: list[Passenger]
    language: str
    currency: str
    price_type: PriceType

    def pb(self) -> Info:
        """(internal) Protobuf data. (`Info`)"""
        return Info(
            data=self.flight_data,
            seat=self.seat,
            trip=self.trip,
            passengers=self.passengers,
        )

    def to_bytes(self) -> bytes:
        """Convert this query to bytes."""
        return self.pb().SerializeToString()

    def to_str(self) -> str:
        """Convert this query to a string."""
        return b64encode(self.to_bytes()).decode("utf-8")

    def _get_tfu_param(self) -> str:
        """Get the tfu parameter for price sorting."""
        if self.price_type == "best":
            # Best: field1=2, sort_type=1 (BEST), field5=20
            sort_pref = SortPreference(field1=2, sort_type=SortType.BEST, field5=20)
        else:  # cheapest
            # Cheapest: field1=2, sort_type=2 (CHEAPEST), field5=21
            sort_pref = SortPreference(field1=2, sort_type=SortType.CHEAPEST, field5=21)

        tfu_data = TfuData(preference=sort_pref, field4=b"")
        # Serialize and manually append field4 empty bytes (0x22 0x00)
        # Protobuf normally skips empty fields, but Google includes this
        serialized = tfu_data.SerializeToString()
        # Append field 4 (wire type 2) with length 0: 0x22 (field 4, type 2) + 0x00 (length 0)
        serialized += bytes([0x22, 0x00])
        # Remove padding to match Google's format
        return b64encode(serialized).decode("utf-8").rstrip("=")

    def url(self) -> str:
        """Get the URL for this query.

        This is generally used for debugging purposes.
        """
        url = (
            "https://www.google.com/travel/flights/search?tfs="
            + self.to_str()
            + "&hl="
            + self.language
            + "&curr="
            + self.currency
        )

        # Always include tfu parameter for price sorting
        url += "&tfu=" + self._get_tfu_param()

        return url

    def params(self) -> dict[str, str]:
        """Create `params` in dictionary form."""
        params = {
            "tfs": self.to_str(),
            "hl": self.language,
            "curr": self.currency,
            "tfu": self._get_tfu_param(),  # Always include tfu parameter
        }
        return params

    def __repr__(self) -> str:
        return "Query(...)"


@dataclass
class FlightQuery:
    date: Union[str, Datetime]
    from_airport: str
    to_airport: str
    max_stops: Optional[int] = None
    airlines: Optional[list[str]] = None

    def pb(self) -> FlightData:
        if isinstance(self.date, str):
            date = self.date
        else:
            date = self.date.strftime("%Y-%m-%d")

        return FlightData(
            date=date,
            from_airport=Airport(airport=self.from_airport),
            to_airport=Airport(airport=self.to_airport),
            max_stops=self.max_stops,
            airlines=self.airlines,
        )

    def _setmaxstops(self, m: Optional[int] = None) -> "FlightQuery":
        if m is not None:
            self.max_stops = m

        return self


class Passengers:
    def __init__(
        self,
        *,
        adults: int = 0,
        children: int = 0,
        infants_in_seat: int = 0,
        infants_on_lap: int = 0,
    ):
        assert sum((adults, children, infants_in_seat, infants_on_lap)) <= 9, "Too many passengers (> 9)"
        assert infants_on_lap <= adults, "Must have at least one adult per infant on lap"

        self.adults = adults
        self.children = children
        self.infants_in_seat = infants_in_seat
        self.infants_on_lap = infants_on_lap

    def pb(self) -> list[Passenger]:
        return [
            *(Passenger.ADULT for _ in range(self.adults)),
            *(Passenger.CHILD for _ in range(self.children)),
            *(Passenger.INFANT_IN_SEAT for _ in range(self.infants_in_seat)),
            *(Passenger.INFANT_ON_LAP for _ in range(self.infants_on_lap)),
        ]


DEFAULT_PASSENGERS = Passengers(adults=1)
SEAT_LOOKUP = {
    "economy": Seat.ECONOMY,
    "premium-economy": Seat.PREMIUM_ECONOMY,
    "business": Seat.BUSINESS,
    "first": Seat.FIRST,
}
TRIP_LOOKUP = {
    "round-trip": Trip.ROUND_TRIP,
    "one-way": Trip.ONE_WAY,
    "multi-city": Trip.MULTI_CITY,
}


def create_query(
    *,
    flights: list[FlightQuery],
    seat: SeatType = "economy",
    trip: TripType = "one-way",
    passengers: Passengers = DEFAULT_PASSENGERS,
    language: Union[str, Literal[""], Language] = "",
    currency: Union[str, Literal[""], Currency] = "",
    max_stops: Optional[int] = None,
    price_type: PriceType = "best",
) -> Query:
    """Create a query.

    Args:
        flights: The flight queries.
        seat: Desired seat type.
        trip: Trip type.
        passengers: Passengers.
        language: Set the language. Use `""` (blank str) to let Google decide.
        currency: Set the currency. Use `""` (blank str) to let Google decide.
        max_stops (optional): Set the maximum stops for every flight query, if present.
        price_type (optional): Price sorting type. "best" or "cheapest".
    """
    return Query(
        flight_data=[flight._setmaxstops(max_stops).pb() for flight in flights],
        seat=SEAT_LOOKUP[seat],
        trip=TRIP_LOOKUP[trip],
        passengers=passengers.pb(),
        language=language,
        currency=currency,
        price_type=price_type,
    )
