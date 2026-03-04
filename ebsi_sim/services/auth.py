import json

from ebsi_sim.schemas import ScopeEnum


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