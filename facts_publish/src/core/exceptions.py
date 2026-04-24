class EBSIError(Exception):
    """
    Represents a custom exception for handling errors specific to EBSI. (Status Code: 500)
    """
    pass

class EBSIDatabaseError(EBSIError):
    """
    Represents an error related to the database.
    """
    pass

class EBSIDuplicateError(EBSIError):
    """
    Represents an error when a duplicate element is encountered.
    """
    pass

class EBSIAuthError(EBSIError):
    """
    Represents an EBSI authentication error (Status Code: 401).
    """
    pass


class EBSIRequestError(EBSIError):
    """
    Represents an error that occurs during an EBSI request.
    """
    pass


class EBSINotFoundError(EBSIError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass
