import ebsiClient from '@/repositories/ebsi_base.ts'

const payloadDidrInvite = {
    "grant_type": "vp_token",
    "presentation_submission": {
        "definition_id": "didr_invite_presentation",
        "descriptor_map": [
            {
                "format": "jwt_vp",
                "id": "didr_invite_credential",
                "path": "$",
                "path_nested": {
                    "format": "jwt_vc",
                    "id": "didr_invite_credential",
                    "path": "$.vp.verifiableCredential[0]"
                }
            }
        ],
        "id": undefined as string | undefined,
    },
    "scope": "openid didr_invite",
    "vp_token": undefined as string | undefined,
}

const payloadDidrWrite = {
    "grant_type": "vp_token",
    "presentation_submission": {
        "definition_id": "didr_invite_presentation",
        "descriptor_map": [
            {
                "format": "jwt_vp",
                "id": "didr_invite_credential",
                "path": "$",
                "path_nested": {
                    "format": "jwt_vc",
                    "id": "didr_invite_credential",
                    "path": "$.vp.verifiableCredential[0]"
                }
            }
        ],
        "id": undefined as string | undefined,
    },
    "scope": "openid didr_invite",
    "vp_token": undefined as string | undefined,
}


export default {
    async authenticate(vpToken: string, scope: string) {
        let payload = undefined
        if(scope == "didr_invite"){
            payload = payloadDidrInvite
        }
        if(!payload){
            return
        }
        payload.vp_token = vpToken
        payload.presentation_submission.id = crypto.randomUUID()
        return await ebsiClient.post('/authorisation/token', payload)
    },

}