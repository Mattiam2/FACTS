import json
from datetime import datetime

import jwt
from jwt import get_unverified_header

from ebsi_sim.repositories.didr import IdentifierRepository, VerificationMethodRepository, \
    VerificationRelationshipRepository


def check_did_is_registered(did: str) -> bool:
    did_repo = IdentifierRepository()
    did_el = did_repo.get(did)
    return did_el is not None

def decode_validate_token(vp_token: str) -> str:
    vp_header = get_unverified_header(vp_token)
    vmethod_id = vp_header["kid"]

    vmethod_repo = VerificationMethodRepository()
    vmethod = vmethod_repo.get(vmethod_id)

    if vmethod.did_controller != vp_header["iss"]:
        raise Exception("Invalid issuer")

    if vmethod.notafter < datetime.now():
        raise Exception("VMethod expired")

    vp_public_key = vmethod.public_key
    vp_decoded = jwt.decode(vp_token, vp_public_key, options={'verify_exp': False, "verify_aud": False})

    identified_did = vp_decoded["sub"]

    vrelationship_repo = VerificationRelationshipRepository()
    vrels = vrelationship_repo.list(identifier_did=identified_did, name="authentication", vmethodid=vmethod_id)

    if vrels is None or len(vrels) == 0:
        raise Exception("VP not valid for this DID")

    return vp_decoded

"""
    const presentation = await this.validateVpJwt(
      vpToken,
      // skip DID resolution:
      customScope === DIDR_INVITE_SCOPE,
      reqId,
      // proofPurpose to be used:
      customScope === TNT_AUTHORISE_SCOPE ? "capabilityInvocation" : undefined,
    ){
        const audience = this.issuer;
        const now = Math.floor(Date.now() / 1000);

        const didAuthenticator = await validateHolder(
            vp,
            iss,
            kid,
            alg,
            iat,
            resolver,
            options?.proofPurpose,
            options?.timeout,
            options?.skipHolderDidResolutionValidation,
            options?.axiosHeaders,
          );
      );
    
    
    };
    
    // `didr_invite`: the client must present a VP containing a valid VerifiableAuthorisationToOnboard VC.
    // This is already done by the PEX library, based on the presentation definition.
    // Verify that the DID is not registered yet.
    if (
      customScope === DIDR_INVITE_SCOPE &&
      (await this.isDidRegistered(vp.holder, reqId))
    ) {
      throw new OAuth2TokenError("invalid_request", {
        errorDescription: `Invalid Verifiable Presentation: DID ${vp.holder} is already registered in the DID Registry`,
      });
    }

    // `didr_write`: the client needs to have entry in DIDR / can prove her signature.
    // This is already done in validateVpJwt.

    // `ledger_invoke`: the credential subject must contain the contract address and the VC issuer must be the smart contract deployer
    if (customScope === LEDGER_INVOKE_SCOPE) {
      const addresses = await this.validateTrustedContractDeployer(
        presentation,
        reqId,
      );
      extraClaims["authorization_details"] = { addresses };
    }

    // `tir_invite`: the client must present a VP containing a valid VerifiableAuthorisationForTrustChain, VerifiableAccreditationToAttest, or VerifiableAccreditationToAccredit.
    // This is already done by the PEX library, based on the presentation definition.
    if (customScope === TIR_INVITE_SCOPE) {
      await this.validateTrustedIssuer(vp.holder, true, reqId);
    }

    // `tir_write`: the client needs to be registered as a Trusted Issuer with accreditations.
    if (customScope === TIR_WRITE_SCOPE) {
      await this.validateTrustedIssuer(vp.holder, false, reqId);
    }

    // `timestamp_write`: the client needs to have entry in DIDR / can prove her signature.
    // This is already done in validateVpJwt.

    // `tnt_authorise`: the client must be have the TNT:authoriseDid attribute in Trusted Policies Registry.
    if (customScope === TNT_AUTHORISE_SCOPE) {
      await this.validateTntAdmin(vp.holder, reqId);
    }

    // `tnt_create`: the client must be an allowlisted TnT Document creator
    if (customScope === TNT_CREATE_SCOPE) {
      await this.validateTntCreator(vp.holder, reqId);
    }

    // `tnt_write`: the client must have granted access for write
    if (customScope === TNT_WRITE_SCOPE) {
      await this.validateTntWriter(vp.holder, reqId);
    }
"""