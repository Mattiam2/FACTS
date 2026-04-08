class EBSIError(Exception):
    """
    Represents a custom exception for handling errors specific to EBSI. (Status Code: 500)
    """
    pass


class AuthError(EBSIError):
    """
    Represents an EBSI authentication error (Status Code: 401).
    """
    pass


class RequestError(EBSIError):
    """
    Represents an error that occurs during an EBSI request.
    """
    pass


class NotFoundError(EBSIError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass
