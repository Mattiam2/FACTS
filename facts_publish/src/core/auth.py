from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel

from facts_publish.src.core.config import settings
from facts_publish.src.core.exceptions import FACTSAuthError, FACTSRequestError

facts_scheme = HTTPBearer(auto_error=False)


class User(SQLModel):
    credential_subject: dict | None = None
    verifiable_credential: str | None = None
    ebsi_access_token: str | None = None
    scopes: list[str] | None = None


def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(facts_scheme)]):
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
        user_data = jwt.decode(token.credentials, settings.AUTH_SECRET_KEY, algorithms=["HS256"],
                          options={'verify_exp': True, "verify_aud": False})
    except jwt.ExpiredSignatureError:
        raise FACTSAuthError("Token expired")
    except jwt.exceptions.DecodeError:
        raise FACTSAuthError("Invalid token")

    if not user_data:
        raise FACTSAuthError("Impossible to authenticate user")

    user_data.pop("exp", None)
    return User.model_validate(user_data)


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
        raise FACTSRequestError("Invalid method")
