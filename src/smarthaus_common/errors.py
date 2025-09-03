class SmarthausError(Exception):
    """Base error for SmartHaus operations."""


class AuthConfigurationError(SmarthausError):
    pass


class GraphRequestError(SmarthausError):
    pass
