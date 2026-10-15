class RouteError(Exception):
    pass


class EmptyRouteError(RouteError):
    pass


class InvalidStopError(RouteError):
    pass


class DuplicateStopError(RouteError):
    pass


class StopNotFoundError(RouteError):
    pass
