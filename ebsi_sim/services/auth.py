from datetime import datetime

import jwt
from fastapi import HTTPException
from jwt import get_unverified_header
from starlette.status import HTTP_400_BAD_REQUEST

from ebsi_sim.repositories.didr import IdentifierRepository, VerificationMethodRepository, \
    VerificationRelationshipRepository
from jsonpath_ng import parse
from jsonschema import validate

from ebsi_sim.schemas.token import PresentationDescriptor, PresentationSubmission


def check_did_is_registered(did: str) -> bool:
    did_repo = IdentifierRepository()
    did_el = did_repo.get(did)
    return did_el is not None

def decode_and_check_signature(token: str, relationship_type: str, credential_algos=None) -> dict:
    token_header = get_unverified_header(token)
    vmethod_id = token_header.get("kid")

    if vmethod_id is None:
        raise Exception("No verification method id found in token header")

    vmethod_repo = VerificationMethodRepository()
    vmethod = vmethod_repo.get(vmethod_id)

    vmethod_public_key = vmethod.public_key
    decoded_token = jwt.decode(token, vmethod_public_key, algorithms=credential_algos, options={'verify_exp': False, 'verify_aud': False, 'verify_signature': False})

    vmethod_issuer = decoded_token.get("iss")
    if vmethod_issuer is None:
        raise Exception("No issuer found in token")

    if vmethod.did_controller != vmethod_issuer:
        raise Exception("Verification method is not owned by the issuer")

    if vmethod.notafter < datetime.now():
        raise Exception("Verification method is expired")


    vrelationship_repo = VerificationRelationshipRepository()
    vrels = vrelationship_repo.list(identifier_did=vmethod_issuer, name=relationship_type, vmethodid=vmethod_id)

    if vrels is None or len(vrels) == 0:
        raise Exception("Verification method not valid for this operation")

    return decoded_token

def find_credential(vp_token, submission: PresentationDescriptor, vp_formats, input_descriptor):
    credential_id = submission.id
    credential_path = submission.path
    credential_format = submission.format

    descriptor_algos = vp_formats.copy()
    descriptor_constraints = []

    if input_descriptor["id"] == credential_id:
        descriptor_algos.update(input_descriptor["format"])
        descriptor_constraints.extend(input_descriptor["constraints"]["fields"])
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Mismatch between presentation definition and input descriptor")

    credential_algo = descriptor_algos[credential_format]["alg"]

    jsonpath_expr = parse(credential_path)
    match_payload = jsonpath_expr.find(vp_token)[0]

    # Decode only if VC because VP is already decoded
    decoded_payload = match_payload.value
    if credential_format in ["jwt_vc_json", "jwt_vc_jwt"]:
        relationship_type = "assertionMethod"
        decoded_payload = decode_and_check_signature(match_payload.value, relationship_type, credential_algo)

    if not submission.path_nested:
        for constraint in descriptor_constraints:
            for const_path in constraint["path"]:
                jsonpath_expr = parse(const_path)
                try:
                    match_field = jsonpath_expr.find(decoded_payload)[0]
                    validate(match_field.value, constraint["filter"])
                except Exception as e:
                    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="VP token is not valid")
        return decoded_payload
    else:
        return find_credential(decoded_payload, submission.path_nested, vp_formats, input_descriptor)


def extract_and_validate_credentials(vp_decoded, presentation_submission: PresentationSubmission, presentation_definition):
    credentials = []
    if len(presentation_definition["input_descriptors"]) > 0:
        for input_descriptor in presentation_definition["input_descriptors"]:
            found_input = False
            for descriptor_map in presentation_submission.descriptor_map:
                if descriptor_map.id == input_descriptor["id"]:
                    vc = find_credential(vp_decoded, descriptor_map, presentation_definition["format"],
                                         input_descriptor)
                    if vc["sub"] != vp_decoded["vp"]["holder"]:
                        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                            detail="Credential subject mismatch with holder")
                    found_input = True
                    credentials.append(vc)
            if not found_input:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid presentation")
    return credentials