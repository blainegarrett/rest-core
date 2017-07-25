"""
REST Errors Types
"""


class RestError(Exception):
    """
    Base Rest Exception
    """


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


class AuthenticationException(RestError):
    """
    401 Unauthorized/Authentication Error
    """
    pass


class BadRequestException(RestError):
    """
    400 Bad Request Error
    """
    pass
