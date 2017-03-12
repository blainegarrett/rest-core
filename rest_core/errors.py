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


class DoesNotExistException(RestError):
    """
    404 Not Found
    """
    pass


class PermissionException(RestError):
    """
    403 Permission Error
    """
    pass
