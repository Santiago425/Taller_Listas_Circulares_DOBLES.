class BusStop:
    def __init__(self, name, minutes):
        self.name = name
        self.minutes = minutes
        self.stop_ahead = self
        self.stop_behind = self

    def is_isolated(self):
        return self.stop_ahead is self and self.stop_behind is self

    def to_dict(self):
        return {
            "name": self.name,
            "minutes": self.minutes,
            "stop_ahead": self.stop_ahead.name,
            "stop_behind": self.stop_behind.name,
        }

    def __repr__(self):
        return f"BusStop({self.name!r}, minutes={self.minutes})"
