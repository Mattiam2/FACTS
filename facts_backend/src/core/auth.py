from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
from sqlmodel import SQLModel

from facts_backend.src.core.config import settings
from facts_backend.src.core.exceptions import FACTSAuthError, FACTSRequestError

facts_scheme = HTTPBearer(auto_error=False)


class UserCredentialSubject(SQLModel):
    """
    Represents the abstract user credential subject field of a FACTS Verifiable Credential, storing user information.

    :ivar id: DID identifier for the legal entity.
    :type id: str
    :ivar company_name: The name of the company.
    :type company_name: str
    :ivar company_address: The physical address of the company.
    :type company_address: str
    :ivar company_vat: The company's VAT number.
    :type company_vat: str
    :ivar company_website: The website URL of the company.
    :type company_website: str
    :ivar company_email: The email address associated with the company.
    :type company_email: str
    """
    id: str
    company_name: str
    company_address: str
    company_vat: str
    company_website: str
    company_email: str


class UserPublisherSubject(UserCredentialSubject):
    """
    This class extends the UserCredentialSubject to incorporate the concept of
    authorized hosts for Publisher Users

    :ivar authorized_hosts: List of hosts that the user is authorized to claim article from.
    :type authorized_hosts: list[str]
    """
    authorized_hosts: list[str]


class UserFactCheckerSubject(UserCredentialSubject):
    """
    This class extends the UserCredentialSubject and is used also to describe the specialization of and who accredited FactCheckers Users.

    :ivar specialization: The area of specialization for the fact checker.
    :type specialization: str
    :ivar accredited_by: The organization or entity that accredits the fact checker.
    :type accredited_by: str
    """
    specialization: str
    accredited_by: str


class User(SQLModel):
    """
    Represents a User model used for authentication and authorization purposes.

    :ivar credential_subject: The subject representing the user's credential, which can
        vary depending on their role (e.g., publisher, fact-checker).
    :ivar verifiable_credential: The user's verifiable credential, stored as a JWT string.
    :ivar ebsi_access_token: The access token associated with the user for EBSI authentication.
    :ivar scopes: A list of scopes defining the user's access permissions.
    """
    credential_subject: UserPublisherSubject | UserFactCheckerSubject | UserCredentialSubject
    verifiable_credential: str
    ebsi_access_token: str
    scopes: list[str]


def get_current_user(security_scopes: SecurityScopes,
                     token: Annotated[HTTPAuthorizationCredentials, Depends(facts_scheme)]):
    """
    Decodes and validates a provided token to authenticate a user and retrieve its
    information.

    :param security_scopes: The security scopes required for the current request.
    :type security_scopes: SecurityScopes
    :param token: A signed token containing user claims used for authentication.
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
    user_obj = User.model_validate(user_data)
    if security_scopes is not None:
        for scope in security_scopes.scopes:
            if scope not in user_obj.scopes:
                raise FACTSAuthError("Not enough permissions")
    return user_obj


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
    if method in method_scopes and user.scopes is not None:
        common_scopes = set(user.scopes) & set(method_scopes[method])
        return len(common_scopes) > 0
    else:
        raise FACTSRequestError("Invalid method")
