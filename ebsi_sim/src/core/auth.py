from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel

from src.core.config import settings
from src.core.exceptions import EBSIAuthError, EBSIRequestError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authorisation/token")


class User(SQLModel):
    """
    Represents the current User entity.

    :ivar scopes: Specifies the list of scopes or permissions assigned
        to the user, which determine the actions the user can perform.
    :type scopes: list[str]
    :ivar sub: Represents the unique identifier (subject) for the user.
    :type sub: str
    """
    scopes: list[str]
    sub: str


vp_scheme = HTTPBearer(auto_error=False)


def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(vp_scheme)]):
    """
    Decodes and validates a provided token to authenticate a user and retrieve its
    information.

    :param token: A signed token containing user claims utilized for authentication.
    :type token: str
    :return: An authenticated User object containing user scopes and subject
        (user identifier).
    :rtype: User
    :raises AuthError: If the token has expired, is invalid, or if user authentication
        fails.
    """
    try:
        user = jwt.decode(token.credentials, settings.AUTH_PUBLIC_KEY, algorithms=["ES256"],
                          options={'verify_exp': settings.JWT_VERIFY_EXP, "verify_aud": False})
    except jwt.ExpiredSignatureError:
        raise EBSIAuthError("Token expired")
    except jwt.exceptions.DecodeError:
        raise EBSIAuthError("Invalid token")

    if not user:
        raise EBSIAuthError("Impossible to authenticate user")

    scopes = []
    if "scp" in user:
        scopes = user["scp"].split(" ")
    return User(scopes=scopes, sub=user["sub"])


def check_scopes(user: User, method: str, method_scopes: dict[str, list[str]]):
    """
    Check if a user has the necessary scopes to access a specific method.

    :param user: The user whose scope assignments are being evaluated against the
                 requirements of the given method.
    :type user: User
    :param method: The name of the method to be checked for scope permissions.
    :type method: str
    :param method_scopes: A dictionary mapping each method name to a list of
                          required scopes for accessing it.
    :type method_scopes: dict[str, list[str]]
    :return: A boolean indicating whether the user has at least one matching scope
             required for the requested method.
    :rtype: bool
    :raises RequestError: Raised when the specified method is not found in the
                          method_scopes dictionary.
    """
    if method in method_scopes:
        common_scopes = set(user.scopes) & set(method_scopes[method])
        return len(common_scopes) > 0
    else:
        raise EBSIRequestError("Invalid method")
