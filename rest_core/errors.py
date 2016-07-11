"""
REST Errors Types
"""


class RestError(Exception):
    """
    Base Rest Exception
    """


class MethodNotAllowed(RestError):
    """
    405 Method Not Allowed
    """

    pass
