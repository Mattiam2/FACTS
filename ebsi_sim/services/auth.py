import json
import math
from datetime import datetime
from uuid import uuid4

import jwt
from fastapi import Depends
from jsonpath_ng import parse
from jsonschema import validate
from jwt import get_unverified_header

from ebsi_sim.core.config import settings
from ebsi_sim.repositories.didr import IdentifierRepository, VerificationMethodRepository, \
    VerificationRelationshipRepository
from ebsi_sim.schemas import ScopeEnum
from ebsi_sim.schemas.token import PresentationDescriptor, PresentationSubmission
from ebsi_sim.schemas.verifiable_presentation import VerifiablePresentationPublic, VerifiablePresentationPayload
from ebsi_sim.schemas.verifiable_credential import VerifiableCredentialPayload
from ebsi_sim.utils import pem_to_jwk


class AuthServiceException(Exception):
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
    def create_access_token(scope: ScopeEnum, subject: str):
        pem_pub_key = settings.public_key
        jwk_pub_key = pem_to_jwk(pem_pub_key)
        kid = jwk_pub_key["kid"] if "kid" in jwk_pub_key else None

        if not kid:
            raise AuthServiceException("Can't create access token")

        expires_in = 7200
        iat = math.floor(datetime.utcnow().timestamp())
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
        private_key = settings.private_key
        algorithm = "ES256"
        headers = {
            "alg": "ES256",
            "kid": kid,
            "typ": "JWT"
        }
        return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)

    @staticmethod
    def create_id_token(subject: str, issuer: str):
        pem_pub_key = settings.public_key
        jwk_pub_key = pem_to_jwk(pem_pub_key)
        kid = jwk_pub_key["kid"]

        expires_in = 7200
        iat = math.floor(datetime.utcnow().timestamp())
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
        private_key = settings.private_key
        algorithm = "ES256"
        headers = {
            "alg": "ES256",
            "kid": kid,
            "typ": "JWT"
        }
        return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)

    @staticmethod
    def load_presentation(scope: ScopeEnum):
        match scope:
            case ScopeEnum.tir_write:
                path = f"ebsi_sim/includes/presentation_tir_write.json"
            case ScopeEnum.tnt_write:
                path = f"ebsi_sim/includes/presentation_tnt_write.json"
            case ScopeEnum.tpr_write:
                path = f"ebsi_sim/includes/presentation_tpr_write.json"
            case ScopeEnum.didr_invite:
                path = f"ebsi_sim/includes/presentation_didr_invite.json"
            case ScopeEnum.didr_write:
                path = f"ebsi_sim/includes/presentation_didr_write.json"
            case ScopeEnum.timestamp_write:
                path = f"ebsi_sim/includes/presentation_timestamp_write.json"
            case ScopeEnum.tir_invite:
                path = f"ebsi_sim/includes/presentation_tir_invite.json"
            case ScopeEnum.tnt_authorise:
                path = f"ebsi_sim/includes/presentation_tnt_authorise.json"
            case ScopeEnum.tnt_create:
                path = f"ebsi_sim/includes/presentation_tnt_create.json"
            case ScopeEnum.tsr_write:
                path = f"ebsi_sim/includes/presentation_tsr_write.json"
            case _:
                raise AuthServiceException("Invalid scope")
        presentation_definition = json.load(open(path, "r"))
        return presentation_definition

    def decode_and_check_signature(self, token: str, relationship_type: str, credential_algos=None) -> dict:
        token_header = get_unverified_header(token)
        vmethod_id = token_header.get("kid")

        if vmethod_id is None:
            raise AuthServiceException("No verification method id found in token header")

        vmethod = self.verification_method_repository.get(vmethod_id)

        if vmethod is None:
            raise AuthServiceException("Verification method not found")

        vmethod_public_key = vmethod.public_key
        decoded_token = jwt.decode(token, vmethod_public_key, algorithms=credential_algos,
                                   options={'verify_exp': False, 'verify_aud': False, 'verify_signature': False})

        vmethod_issuer = decoded_token["iss"]
        if vmethod_issuer is None:
            raise AuthServiceException("No issuer found in token")

        if vmethod.did_controller != vmethod_issuer:
            raise AuthServiceException("Verification method is not owned by the issuer")

        if vmethod.notafter < datetime.now():
            raise AuthServiceException("Verification method is expired")

        vrels = self.verification_relationship_repository.list(identifier_did=vmethod_issuer, name=relationship_type,
                                                               vmethodid=vmethod_id)

        if vrels is None or len(vrels) == 0:
            raise AuthServiceException("Verification method not valid for this operation")

        return decoded_token

    def find_credential(self, vp_payload: VerifiablePresentationPayload, submission: PresentationDescriptor, vp_formats, input_descriptor) -> VerifiableCredentialPayload:
        credential_id = submission.id
        credential_path = submission.path
        credential_format = submission.format

        descriptor_algos = vp_formats.copy()
        descriptor_constraints = []

        if "id" in input_descriptor and input_descriptor["id"] == credential_id:
            if "format" not in input_descriptor or "constraints" not in input_descriptor or "fields" not in \
                    input_descriptor["constraints"]:
                raise AuthServiceException("Missing format or constraints in input descriptor")
            descriptor_algos.update(input_descriptor["format"])
            descriptor_constraints.extend(input_descriptor["constraints"]["fields"])
        else:
            raise AuthServiceException("Mismatch between presentation definition and input descriptor")

        if "alg" not in descriptor_algos[credential_format]:
            raise AuthServiceException("Missing alg in format")
        credential_algo = descriptor_algos[credential_format]["alg"]

        jsonpath_expr = parse(credential_path)
        match_payload = jsonpath_expr.find(vp_payload.model_dump_json())[0]

        # Decode only if VC because VP is already decoded
        decoded_payload = match_payload.value
        if credential_format in ["jwt_vc_json", "jwt_vc_jwt"]:
            relationship_type = "assertionMethod"
            decoded_payload = self.decode_and_check_signature(match_payload.value, relationship_type, credential_algo)

        if not submission.path_nested:
            for constraint in descriptor_constraints:
                if "path" not in constraint or "filter" not in constraint:
                    raise AuthServiceException("Missing path or filter in constraint")
                for const_path in constraint["path"]:
                    jsonpath_expr = parse(const_path)
                    try:
                        match_field = jsonpath_expr.find(decoded_payload)[0]
                        validate(match_field.value, constraint["filter"])
                    except Exception as e:
                        raise AuthServiceException("VP token is not valid")
            credential = VerifiableCredentialPayload(**decoded_payload)
            return credential
        else:
            return self.find_credential(decoded_payload, submission.path_nested, vp_formats, input_descriptor)

    def extract_and_validate_credentials(self, vp_decoded: VerifiablePresentationPayload, presentation_submission: PresentationSubmission,
                                         presentation_definition) -> list[VerifiableCredentialPayload]:
        credentials = []
        if "input_descriptors" in presentation_definition and len(presentation_definition["input_descriptors"]) > 0:
            for input_descriptor in presentation_definition["input_descriptors"]:
                found_input = False
                for descriptor_map in presentation_submission.descriptor_map:
                    if "id" in input_descriptor and descriptor_map.id == input_descriptor["id"]:
                        if vp_decoded.vp is None or vp_decoded.vp.holder is None:
                            raise AuthServiceException("Invalid VP")
                        cred: VerifiableCredentialPayload = self.find_credential(vp_decoded, descriptor_map, presentation_definition["format"],
                                                  input_descriptor)
                        if cred.sub is None:
                            raise AuthServiceException("Invalid VC")
                        if cred.sub != vp_decoded.vp.holder:
                            raise AuthServiceException("Credential subject mismatch with holder")
                        found_input = True
                        credentials.append(cred)
                if not found_input:
                    raise AuthServiceException("Invalid presentation")
        return credentials
