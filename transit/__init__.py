from .bus_line import BusLine
from .bus_stop import BusStop
from .circular_route import CircularRoute
from .errors import (
    DuplicateStopError,
    EmptyRouteError,
    InvalidStopError,
    RouteError,
    StopNotFoundError,
)

SAMPLE_STOPS = [
    ("Terminal", 5),
    ("Universidad", 4),
    ("Hospital", 6),
    ("Parque Central", 3),
    ("Centro Comercial", 7),
    ("Estadio", 5),
]


def build_sample_line():
    line = BusLine("Ruta Circular Universitaria")
    for name, minutes in SAMPLE_STOPS:
        line.add_stop(name, minutes)
    return line
