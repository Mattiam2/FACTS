class FACTSError(Exception):
    """
    Represents a custom exception for handling errors specific to EBSI. (Status Code: 500)
    """
    pass

class FACTSDatabaseError(FACTSError):
    """
    Represents an error related to the database.
    """
    pass

class FACTSDuplicateError(FACTSError):
    """
    Represents an error when a duplicate element is encountered.
    """
    pass

class FACTSAuthError(FACTSError):
    """
    Represents an EBSI authentication error (Status Code: 401).
    """
    pass


class FACTSRequestError(FACTSError):
    """
    Represents an error that occurs during an EBSI request.
    """
    pass


class FACTSNotFoundError(FACTSError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass
