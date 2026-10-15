from .circular_route import CircularRoute
from .errors import EmptyRouteError, InvalidStopError

POSITIONS = ("start", "end", "after")


class BusLine:
    def __init__(self, name):
        self.route = CircularRoute(name)
        self.bus_at = None
        self.laps = 0
        self.elapsed_minutes = 0

    def add_stop(self, name, minutes, position="end", reference=None):
        if position == "start":
            stop = self.route.insert_at_start(name, minutes)
        elif position == "end":
            stop = self.route.insert_at_end(name, minutes)
        elif position == "after":
            if not reference:
                raise InvalidStopError("Debes indicar después de qué parada va la nueva")
            stop = self.route.insert_after(reference, name, minutes)
        else:
            raise InvalidStopError("La posición debe ser inicio, final o después de otra parada")
        if self.bus_at is None:
            self.bus_at = stop
        return stop

    def remove_stop(self, name):
        stop = self.route.find(name)
        if stop is self.bus_at:
            self.bus_at = stop.stop_ahead if self.route.size > 1 else None
        return self.route.remove(name)

    def find_stop(self, name):
        return self.route.find(name)

    def drive_ahead(self):
        self._require_stops()
        self.elapsed_minutes += self.bus_at.minutes
        if self.bus_at.stop_ahead is self.route.terminal:
            self.laps += 1
        self.bus_at = self.bus_at.stop_ahead
        return self.bus_at

    def drive_behind(self):
        self._require_stops()
        self.elapsed_minutes += self.bus_at.stop_behind.minutes
        self.bus_at = self.bus_at.stop_behind
        return self.bus_at

    def snapshot(self):
        bus_at = self.bus_at
        return {
            "name": self.route.name,
            "size": self.route.size,
            "laps": self.laps,
            "elapsed_minutes": self.elapsed_minutes,
            "total_minutes": self.route.total_minutes(),
            "terminal": self.route.terminal.name if self.route.terminal else None,
            "bus_at": bus_at.to_dict() if bus_at else None,
            "stops": [stop.to_dict() for stop in self.route.traverse_ahead()],
            "ahead": [stop.name for stop in self.route.traverse_ahead(bus_at)],
            "behind": [stop.name for stop in self.route.traverse_behind(bus_at)],
        }

    def _require_stops(self):
        if self.bus_at is None:
            raise EmptyRouteError("La ruta no tiene paradas")
