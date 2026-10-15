from .bus_stop import BusStop
from .errors import DuplicateStopError, EmptyRouteError, InvalidStopError, StopNotFoundError

MAX_NAME_LENGTH = 30
MAX_MINUTES = 120


class CircularRoute:
    def __init__(self, name):
        self.name = name
        self.terminal = None
        self.size = 0

    def __len__(self):
        return self.size

    def is_empty(self):
        return self.terminal is None

    def insert_at_start(self, name, minutes):
        stop = self._build_stop(name, minutes)
        if self.is_empty():
            self.terminal = stop
        else:
            self._link_after(self.terminal.stop_behind, stop)
            self.terminal = stop
        self.size += 1
        return stop

    def insert_at_end(self, name, minutes):
        stop = self._build_stop(name, minutes)
        if self.is_empty():
            self.terminal = stop
        else:
            self._link_after(self.terminal.stop_behind, stop)
        self.size += 1
        return stop

    def insert_after(self, reference_name, name, minutes):
        reference = self.find(reference_name)
        stop = self._build_stop(name, minutes)
        self._link_after(reference, stop)
        self.size += 1
        return stop

    def find(self, name):
        if self.is_empty():
            raise EmptyRouteError("La ruta no tiene paradas")
        stop = self._locate(str(name).strip())
        if stop is None:
            raise StopNotFoundError(f"La parada '{name}' no existe en la ruta")
        return stop

    def remove(self, name):
        stop = self.find(name)
        if self.size == 1:
            self.terminal = None
        else:
            stop.stop_behind.stop_ahead = stop.stop_ahead
            stop.stop_ahead.stop_behind = stop.stop_behind
            if stop is self.terminal:
                self.terminal = stop.stop_ahead
        stop.stop_ahead = stop
        stop.stop_behind = stop
        self.size -= 1
        return stop

    def traverse_ahead(self, start=None):
        return self._traverse(start, lambda stop: stop.stop_ahead)

    def traverse_behind(self, start=None):
        return self._traverse(start, lambda stop: stop.stop_behind)

    def total_minutes(self):
        return sum(stop.minutes for stop in self.traverse_ahead())

    def is_consistent(self):
        if self.is_empty():
            return self.size == 0
        stop = self.terminal
        for _ in range(self.size):
            if stop.stop_ahead.stop_behind is not stop or stop.stop_behind.stop_ahead is not stop:
                return False
            stop = stop.stop_ahead
        return stop is self.terminal

    def _traverse(self, start, step):
        if self.is_empty():
            return []
        stop = start or self.terminal
        visited = []
        for _ in range(self.size):
            visited.append(stop)
            stop = step(stop)
        return visited

    def _locate(self, name):
        if self.is_empty():
            return None
        stop = self.terminal
        for _ in range(self.size):
            if stop.name.lower() == name.lower():
                return stop
            stop = stop.stop_ahead
        return None

    def _link_after(self, reference, stop):
        stop.stop_behind = reference
        stop.stop_ahead = reference.stop_ahead
        reference.stop_ahead.stop_behind = stop
        reference.stop_ahead = stop

    def _build_stop(self, name, minutes):
        name = str(name or "").strip()
        if not name:
            raise InvalidStopError("El nombre de la parada es obligatorio")
        if len(name) > MAX_NAME_LENGTH:
            raise InvalidStopError(f"El nombre no puede tener más de {MAX_NAME_LENGTH} caracteres")
        if self._locate(name):
            raise DuplicateStopError(f"Ya existe una parada llamada '{name}'")
        try:
            minutes = int(minutes)
        except (TypeError, ValueError):
            raise InvalidStopError("Los minutos deben ser un número entero")
        if not 1 <= minutes <= MAX_MINUTES:
            raise InvalidStopError(f"Los minutos deben estar entre 1 y {MAX_MINUTES}")
        return BusStop(name, minutes)
