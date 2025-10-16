from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Seat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_SEAT: _ClassVar[Seat]
    ECONOMY: _ClassVar[Seat]
    PREMIUM_ECONOMY: _ClassVar[Seat]
    BUSINESS: _ClassVar[Seat]
    FIRST: _ClassVar[Seat]

class Trip(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_TRIP: _ClassVar[Trip]
    ROUND_TRIP: _ClassVar[Trip]
    ONE_WAY: _ClassVar[Trip]
    MULTI_CITY: _ClassVar[Trip]

class Passenger(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_PASSENGER: _ClassVar[Passenger]
    ADULT: _ClassVar[Passenger]
    CHILD: _ClassVar[Passenger]
    INFANT_IN_SEAT: _ClassVar[Passenger]
    INFANT_ON_LAP: _ClassVar[Passenger]

class SortType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_SORT: _ClassVar[SortType]
    BEST: _ClassVar[SortType]
    CHEAPEST: _ClassVar[SortType]
UNKNOWN_SEAT: Seat
ECONOMY: Seat
PREMIUM_ECONOMY: Seat
BUSINESS: Seat
FIRST: Seat
UNKNOWN_TRIP: Trip
ROUND_TRIP: Trip
ONE_WAY: Trip
MULTI_CITY: Trip
UNKNOWN_PASSENGER: Passenger
ADULT: Passenger
CHILD: Passenger
INFANT_IN_SEAT: Passenger
INFANT_ON_LAP: Passenger
UNKNOWN_SORT: SortType
BEST: SortType
CHEAPEST: SortType

class Airport(_message.Message):
    __slots__ = ("airport",)
    AIRPORT_FIELD_NUMBER: _ClassVar[int]
    airport: str
    def __init__(self, airport: _Optional[str] = ...) -> None: ...

class FlightData(_message.Message):
    __slots__ = ("date", "from_airport", "to_airport", "max_stops", "airlines")
    DATE_FIELD_NUMBER: _ClassVar[int]
    FROM_AIRPORT_FIELD_NUMBER: _ClassVar[int]
    TO_AIRPORT_FIELD_NUMBER: _ClassVar[int]
    MAX_STOPS_FIELD_NUMBER: _ClassVar[int]
    AIRLINES_FIELD_NUMBER: _ClassVar[int]
    date: str
    from_airport: Airport
    to_airport: Airport
    max_stops: int
    airlines: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, date: _Optional[str] = ..., from_airport: _Optional[_Union[Airport, _Mapping]] = ..., to_airport: _Optional[_Union[Airport, _Mapping]] = ..., max_stops: _Optional[int] = ..., airlines: _Optional[_Iterable[str]] = ...) -> None: ...

class Info(_message.Message):
    __slots__ = ("data", "seat", "passengers", "trip")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SEAT_FIELD_NUMBER: _ClassVar[int]
    PASSENGERS_FIELD_NUMBER: _ClassVar[int]
    TRIP_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[FlightData]
    seat: Seat
    passengers: _containers.RepeatedScalarFieldContainer[Passenger]
    trip: Trip
    def __init__(self, data: _Optional[_Iterable[_Union[FlightData, _Mapping]]] = ..., seat: _Optional[_Union[Seat, str]] = ..., passengers: _Optional[_Iterable[_Union[Passenger, str]]] = ..., trip: _Optional[_Union[Trip, str]] = ...) -> None: ...

class Price(_message.Message):
    __slots__ = ("price", "currency")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    price: int
    currency: str
    def __init__(self, price: _Optional[int] = ..., currency: _Optional[str] = ...) -> None: ...

class ItinerarySummary(_message.Message):
    __slots__ = ("flights", "price")
    FLIGHTS_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    flights: str
    price: Price
    def __init__(self, flights: _Optional[str] = ..., price: _Optional[_Union[Price, _Mapping]] = ...) -> None: ...

class SortPreference(_message.Message):
    __slots__ = ("field1", "sort_type", "field5")
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    SORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIELD5_FIELD_NUMBER: _ClassVar[int]
    field1: int
    sort_type: SortType
    field5: int
    def __init__(self, field1: _Optional[int] = ..., sort_type: _Optional[_Union[SortType, str]] = ..., field5: _Optional[int] = ...) -> None: ...

class TfuData(_message.Message):
    __slots__ = ("preference", "field4")
    PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    FIELD4_FIELD_NUMBER: _ClassVar[int]
    preference: SortPreference
    field4: bytes
    def __init__(self, preference: _Optional[_Union[SortPreference, _Mapping]] = ..., field4: _Optional[bytes] = ...) -> None: ...
