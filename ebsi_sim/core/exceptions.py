class EBSIError(Exception):
    pass

class ServerError(EBSIError):
    pass

class AuthError(EBSIError):
    pass

class RequestError(EBSIError):
    pass

class NotFoundError(EBSIError):
    pass