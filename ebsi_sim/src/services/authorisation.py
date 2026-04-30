import json
import math
from datetime import datetime
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives.asymmetric.ec import SECP256K1, EllipticCurvePublicKey
from fastapi import Depends
from jsonpath_ng import parse
from jsonschema import validate
from jwt import get_unverified_header
from jwt.algorithms import ECAlgorithm

from ebsi_sim.src.core.config import settings
from ebsi_sim.src.core.exceptions import EBSIAuthError, EBSINotFoundError, EBSIRequestError, EBSIError
from ebsi_sim.src.models.didr import Identifier
from ebsi_sim.src.repositories.didr import IdentifierRepository, VerificationMethodRepository, \
    VerificationRelationshipRepository
from ebsi_sim.src.schemas import ScopeEnum
from ebsi_sim.src.schemas.token import PresentationDescriptor, PresentationSubmission, TokenCreate
from ebsi_sim.src.schemas.verifiable_credential import VerifiableCredentialPayload
from ebsi_sim.src.schemas.verifiable_presentation import VerifiablePresentationPayload
from ebsi_sim.src.utils import pem_to_jwk


class AuthServiceError(EBSIError):
    """
    Represents an error specific to AUTH service operations (Status Code: 500).
    """
    pass


class AuthServiceAuthError(AuthServiceError, EBSIAuthError):
    """
    Represents an AUTH service authentication error (Status Code: 401).
    """
    pass


class AuthServiceNotFoundError(AuthServiceError, EBSINotFoundError):
    """
    Represents an error raised when a specific resource is not found (Status Code: 404).
    """
    pass


class AuthServiceRequestError(AuthServiceError, EBSIRequestError):
    """
    Represents an error that occurs during an AUTH service request.
    """
    pass


class AuthService:
    identifier_repository: IdentifierRepository
    verification_method_repository: VerificationMethodRepository
    verification_relationship_repository: VerificationRelationshipRepository

    def __init__(self, identifier_repository: IdentifierRepository = Depends(),
                 verification_method_repository: VerificationMethodRepository = Depends(),
                 verification_relationship_repository: VerificationRelationshipRepository = Depends()):
        self.identifier_repository = identifier_repository
        self.verification_method_repository = verification_method_repository
        self.verification_relationship_repository = verification_relationship_repository

    @staticmethod
    def generate_access_token(scope: ScopeEnum, subject: str) -> str:
        """
        Generates a JWT access token with the specified scope and subject.

        :param scope: The scope of the access token.
        :type scope: ScopeEnum
        :param subject: The subject of the token (DID)
        :type subject: str
        :return: The signed JWT access token as a JWT string.
        :rtype: str
        :raises AuthServiceError: If the public key does not include a valid
            Key ID (`kid`).
        """

        # Authorisation Service Public Key
        pem_pub_key = settings.AUTH_PUBLIC_KEY
        jwk_pub_key = pem_to_jwk(pem_pub_key)
        kid = jwk_pub_key["kid"] if "kid" in jwk_pub_key else None

        if not kid:
            raise AuthServiceError("Can't create access token")

        expires_in = 7200
        iat = math.floor(datetime.now().timestamp())
        exp = iat + expires_in

        payload = {
            "aud": "https://api-pilot.ebsi.eu/authorisation/v4",
            "exp": exp,
            "iat": iat,
            "iss": "https://api-pilot.ebsi.eu/authorisation/v4",
            "jti": str(uuid4()),
            "scp": scope,
            "sub": subject,
        }
        private_key = settings.AUTH_PRIVATE_KEY
        algorithm = "ES256"
        headers = {
            "alg": "ES256",
            "kid": kid,
            "typ": "JWT"
        }
        return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)

    @staticmethod
    def generate_id_token(subject: str, issuer: str) -> str:
        """
        Generates a JWT ID token with the specified subject and issuer.

        :param subject: The unique identifier of the subject for whom the token is being
            generated.
        :type subject: str
        :param issuer: The identifier of the entity that is issuing the token.
        :type issuer: str
        :return: A signed JWT ID token containing the encoded claims and additional headers.
        :rtype: str
        :raises AuthServiceError: If the public key does not include a valid
            Key ID (`kid`).
        """
        pem_pub_key = settings.AUTH_PUBLIC_KEY
        jwk_pub_key = pem_to_jwk(pem_pub_key)
        kid = jwk_pub_key["kid"] if "kid" in jwk_pub_key else None

        if not kid:
            raise AuthServiceError("Can't create ID token")

        expires_in = 7200
        iat = math.floor(datetime.now().timestamp())
        exp = iat + expires_in

        payload = {
            "aud": issuer,
            "exp": exp,
            "iat": iat,
            "iss": "https://api-pilot.ebsi.eu/authorisation/v4",
            "jti": str(uuid4()),
            "nonce": 0,
            "sub": subject,
        }
        private_key = settings.AUTH_PRIVATE_KEY
        algorithm = "ES256"
        headers = {
            "alg": "ES256",
            "kid": kid,
            "typ": "JWT"
        }
        return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)

    @staticmethod
    def load_presentation(scope: ScopeEnum) -> dict:
        """
        Loads a JSON-formatted presentation definition based on the provided scope.

        :param scope: The specific scope used to determine the presentation definition
                      to load.
        :type scope: ScopeEnum
        :return: The loaded presentation definition.
        :rtype: dict
        :raises AuthServiceError: If the scope is invalid or there is an error loading
                                   the presentation definition file.
        """
        match scope:
            case ScopeEnum.tir_write:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tir_write.json"
            case ScopeEnum.tnt_write:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tnt_write.json"
            case ScopeEnum.tpr_write:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tpr_write.json"
            case ScopeEnum.didr_invite:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_didr_invite.json"
            case ScopeEnum.didr_write:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_didr_write.json"
            case ScopeEnum.timestamp_write:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_timestamp_write.json"
            case ScopeEnum.tir_invite:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tir_invite.json"
            case ScopeEnum.tnt_authorise:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tnt_authorise.json"
            case ScopeEnum.tnt_create:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tnt_create.json"
            case ScopeEnum.tsr_write:
                path = f"{settings.PROJECT_ROOT}/includes/presentation_tsr_write.json"
            case _:
                raise AuthServiceError("Invalid scope")
        try:
            presentation_definition = json.load(open(path, "r"))
        except Exception as e:
            raise AuthServiceError(f"Error loading presentation definition: {e}")
        return presentation_definition

    def decode_and_check_signature(self, token: str, relationship_type: str, credential_algos=None,
                                   check_signature=True) -> dict:
        """
        Decodes a given token, optionally verifies its signature and checks its validity based on the
        verification method and relationships.

        :param token: The JWT token to be decoded and verified.
        :type token: str
        :param relationship_type: The type of relationship to check the verification method against.
        :type relationship_type: str
        :param credential_algos: The set of supported algorithms for verifying the signature. Defaults to None.
        :type credential_algos: list, optional
        :param check_signature: Indicates whether to verify the token's signature. Defaults to True.
        :type check_signature: bool
        :returns: A dictionary containing the decoded contents of the token.
        :rtype: dict
        """
        if check_signature:
            token_header = get_unverified_header(token)
            vmethod_id = token_header.get("kid")

            if vmethod_id is None:
                raise AuthServiceError("No verification method id found in token header")

            vmethod = self.verification_method_repository.get(vmethod_id)

            if vmethod is None:
                raise AuthServiceError("Verification method not found")

            vmethod_public_key_bytes = bytes.fromhex(vmethod.public_key.replace("0x", ""))
            if vmethod.issecp256k1:
                vmethod_public_key = EllipticCurvePublicKey.from_encoded_point(
                    SECP256K1(),
                    vmethod_public_key_bytes
                )
            else:
                vmethod_public_key_string = vmethod_public_key_bytes.decode('utf-8')
                vmethod_public_key = ECAlgorithm.from_jwk(vmethod_public_key_string)

            try:
                decoded_token = jwt.decode(token, vmethod_public_key, algorithms=credential_algos,
                                           options={'verify_exp': settings.JWT_VERIFY_EXP, 'verify_aud': False, 'verify_signature': True})
            except jwt.exceptions.InvalidSignatureError:
                raise AuthServiceRequestError("Invalid signature")

            vmethod_issuer = decoded_token["iss"] #Issuer della credential
            if vmethod_issuer is None:
                raise AuthServiceRequestError("No issuer found in token")

            if vmethod.did_controller != vmethod_issuer: #Issuer della credential corrisponde al did_controller del vmethod usato?
                raise AuthServiceRequestError("Verification method is not owned by the issuer")

            if vmethod.notafter < datetime.now():
                raise AuthServiceRequestError("Verification method is expired")

            vrels = self.verification_relationship_repository.list(identifier_did=vmethod_issuer,
                                                                   name=relationship_type,
                                                                   vmethodid=vmethod_id)

            if vrels is None or len(vrels) == 0:
                raise AuthServiceRequestError("Verification method not valid for this operation")

        else:
            decoded_token = jwt.decode(token,
                                       options={'verify_exp': settings.JWT_VERIFY_EXP, 'verify_aud': False, 'verify_signature': False})

        return decoded_token

    def find_credential(self, vp_payload: VerifiablePresentationPayload, submission: PresentationDescriptor, vp_formats,
                        input_descriptor) -> VerifiableCredentialPayload:
        """
        Finds and validates a credential inside a Verifiable Presentation Payload based on a provided
        presentation submission descriptor and input descriptor. The function decodes and validates
        credentials against defined constraints in the input descriptor.

        :param vp_payload: The Verifiable Presentation Payload object containing the data to be validated.
        :type vp_payload: VerifiablePresentationPayload
        :param submission: The Presentation Descriptor describing the credential and its location.
        :type submission: PresentationDescriptor
        :param vp_formats: A dictionary containing format definitions used for validating credentials.
        :type vp_formats: dict
        :param input_descriptor: The credential input descriptor containing constraints and format
            definitions required for the credential validation.
        :type input_descriptor: dict
        :return: A valid Verifiable Credential payload that matches the input descriptor and passes
            all defined constraints.
        :rtype: VerifiableCredentialPayload

        :raises AuthServiceError: Raised when required format or constraints are missing in the
            input descriptor.
        :raises AuthServiceRequestError: Raised when there is a mismatch between the presentation
            definition ID and the input descriptor ID, or when required fields for validation
            (such as algorithm or constraints) are missing or violated.
        """
        credential_id = submission.id
        credential_path = submission.path
        credential_format = submission.format

        descriptor_algos = vp_formats.copy()
        descriptor_constraints = []

        if "id" in input_descriptor and input_descriptor["id"] == credential_id:
            if "format" not in input_descriptor or "constraints" not in input_descriptor or "fields" not in \
                    input_descriptor["constraints"]:
                raise AuthServiceError("Missing format or constraints in input descriptor")
            descriptor_algos.update(input_descriptor["format"])
            descriptor_constraints.extend(input_descriptor["constraints"]["fields"])
        else:
            raise AuthServiceRequestError("Mismatch between presentation definition id and input descriptor id")

        if "alg" not in descriptor_algos[credential_format]:
            raise AuthServiceRequestError("Missing alg in format")
        credential_algo = descriptor_algos[credential_format]["alg"]

        jsonpath_expr = parse(credential_path)
        match_payload = jsonpath_expr.find(json.loads(vp_payload.model_dump_json()))[0]

        # Decode only if VC because VP is already decoded
        decoded_payload = match_payload.value
        if credential_format in ["jwt_vc_json", "jwt_vc"]:
            relationship_type = "assertionMethod"
            decoded_payload = self.decode_and_check_signature(match_payload.value, relationship_type, credential_algo)

        if not submission.path_nested:
            for constraint in descriptor_constraints:
                if "path" not in constraint or "filter" not in constraint:
                    raise AuthServiceRequestError("Missing path or filter in constraint")
                for const_path in constraint["path"]:
                    jsonpath_expr = parse(const_path)
                    try:
                        match_field = jsonpath_expr.find(decoded_payload)[0]
                        validate(match_field.value, constraint["filter"])
                    except Exception:
                        raise AuthServiceRequestError("Presentation definition constraints violated in payload")
            credential = VerifiableCredentialPayload(**decoded_payload)
            return credential
        else:
            vp_payload = VerifiablePresentationPayload(**decoded_payload)
            return self.find_credential(vp_payload, submission.path_nested, vp_formats, input_descriptor)

    def extract_and_validate_credentials(self, vp_decoded: VerifiablePresentationPayload,
                                         presentation_submission: PresentationSubmission,
                                         presentation_definition: dict) -> list[VerifiableCredentialPayload]:
        credentials = []
        if "input_descriptors" in presentation_definition and len(presentation_definition["input_descriptors"]) > 0:
            for input_descriptor in presentation_definition["input_descriptors"]:
                found_input = False
                for descriptor_map in presentation_submission.descriptor_map:
                    if "id" in input_descriptor and descriptor_map.id == input_descriptor["id"]:
                        if vp_decoded.vp is None or vp_decoded.vp.holder is None:
                            raise AuthServiceError("Invalid VP")
                        cred: VerifiableCredentialPayload = self.find_credential(vp_decoded, descriptor_map,
                                                                                 presentation_definition["format"],
                                                                                 input_descriptor)
                        if cred.sub is None:
                            raise AuthServiceRequestError("Invalid credential: missing subject")
                        if cred.sub != vp_decoded.vp.holder:
                            raise AuthServiceRequestError("Invalid credential: credential subject mismatch with holder")
                        found_input = True
                        credentials.append(cred)
                if not found_input:
                    raise AuthServiceRequestError("Invalid presentation")

        return credentials

    def get_verifiable_presentation(self, payload: TokenCreate) -> VerifiablePresentationPayload:
        """
        Decodes and validates a Verifiable Presentation (VP) from the given payload. It checks the signature
        of the presentation, and verifies key attributes such as subject and holder for correctness.

        :param payload: The token creation payload that contains the verifiable presentation token.
        :type payload: TokenCreate
        :return: A decoded and validated VerifiablePresentationPayload object.
        :rtype: VerifiablePresentationPayload
        :raises AuthServiceRequestError: If the VP token is invalid or the subject/holder attributes are
            incorrect or inconsistent.
        :raises EBSIError: If there is an issue decoding or processing the VP token.
        """
        try:
            check_signature = (payload.scope != ScopeEnum.didr_invite)
            vp_decoded = self.decode_and_check_signature(payload.vp_token, "authentication",
                                                         credential_algos=['ES256', 'ES256K'],
                                                         check_signature=check_signature)

            vp_payload = VerifiablePresentationPayload(**vp_decoded)

            if vp_payload.sub is None:
                raise AuthServiceRequestError("Invalid VP: missing subject")

            if vp_payload.vp is None or vp_payload.vp.holder is None:
                raise AuthServiceRequestError("Invalid VP: missing holder")

            if vp_payload.sub != vp_payload.vp.holder:
                raise AuthServiceRequestError("Invalid VP: VP Subject mismatch with holder")
        except EBSIError:
            raise
        except Exception as e:
            raise EBSIError(f"Error decoding VP")
        else:
            return vp_payload

    @staticmethod
    def check_scope_constraints(payload: TokenCreate, subject_did: Identifier | None = None) -> None:
        """
        Check if the provided payload's scope and the respective constraints are valid with respect to the
        subject DID.

        :param payload: The token payload to validate.
        :type payload: TokenCreate
        :param subject_did: The subject DID for which the validation is being
            performed. This can be `None` if no subject DID is associated.
        :type subject_did: Identifier | None
        :return: None. The method raises exceptions if constraints are violated.
        :rtype: None
        :raises AuthServiceRequestError: When the scope is `didr_invite` and the `subject_did` is already
            registered, or when the scope is not `didr_invite` and no `subject_did` is provided.
        :raises AuthServiceAuthError: When the scope is `tnt_create` and the `subject_did` is not
            authorized for the specified scope.
        """
        if payload.scope == ScopeEnum.didr_invite and subject_did:
            raise AuthServiceRequestError("DID is already registered")
        elif payload.scope != ScopeEnum.didr_invite and not subject_did:
            raise AuthServiceRequestError("DID is not registered")
        elif (payload.scope == ScopeEnum.tnt_create or payload.scope == ScopeEnum.tnt_write) and not subject_did.tnt_authorized:
            raise AuthServiceAuthError("DID not authorized to this scope")

    def create_token(self, vp_payload: VerifiablePresentationPayload, scope: ScopeEnum,
                     presentation_submission: PresentationSubmission,
                     presentation_definition: dict) -> tuple[str, str]:
        """
        Generates an access token and an ID token based on the provided Verifiable Presentation payload,
        scope, presentation submission, and presentation definition. This function validates the
        presentation definition, extracts credentials if required, and ensures the correctness of the
        subject and issuer information before generating the tokens.

        :param vp_payload: A Verifiable Presentation payload containing the subject and issuer data to
            be used in token generation.
        :type vp_payload: VerifiablePresentationPayload
        :param scope: Scope of the token request specifying the level of access required.
        :type scope: ScopeEnum
        :param presentation_submission: The presentation submission object containing data used to validate
            and extract credentials from the payload.
        :type presentation_submission: PresentationSubmission
        :param presentation_definition: A dictionary outlining the presentation definition used for
            validation of the input descriptors and alignment with the presentation submission.
        :type presentation_definition: dict
        :return: A tuple containing the generated access token and ID token.
        :rtype: tuple
        :raises AuthServiceRequestError: If the presentation definition does not match the ID in
            the presentation submission.
        :raises AuthServiceAuthError: If the credentials are invalid, missing, or extraction fails.
        :raises AuthServiceError: If other unexpected errors occur during token generation.
        """
        try:
            if presentation_submission.definition_id != presentation_definition["id"]:
                raise AuthServiceRequestError("Invalid presentation definition")

            credentials_required = ("input_descriptors" in presentation_definition and len(
                presentation_definition["input_descriptors"]) > 0)

            credential_subject = vp_payload.sub
            credential_issuer = vp_payload.iss
            if credentials_required:
                credentials = self.extract_and_validate_credentials(vp_payload, presentation_submission,
                                                                    presentation_definition)

                if not credentials or len(credentials) == 0:
                    raise AuthServiceAuthError("Invalid credentials")
                else:
                    credential_subject = credentials[0].sub
                    credential_issuer = credentials[0].iss

            access_token = AuthService.generate_access_token(scope, credential_subject)

            id_token = AuthService.generate_id_token(subject=credential_subject, issuer=credential_issuer)
        except EBSIError:
            raise
        except Exception as e:
            raise AuthServiceError(f"Error creating access token")
        else:
            return access_token, id_token
