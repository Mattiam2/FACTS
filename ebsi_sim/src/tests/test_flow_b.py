from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.didr import Identifier, VerificationMethod, VerificationRelationship

@pytest.fixture(name="default_data")
def prepare_data(session: Session):
    """
    Create and prepare default data for testing by populating the database with a set of
    identifier, verification methods, and associated relationships.
    """
    identifier = Identifier(
        did="did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        context='{"@context":["https://www.w3.org/ns/did/v1","https://w3id.org/security/suites/jws-2020/v1"]}',
        tir_authorized=False,
        tnt_authorized=False
    )
    vmethod = VerificationMethod(
        id="did:ebsi:z95paQoBwGAqnnu4RKTmCtT#axZAOKbj-YyMiIN2CRLCwPjSCgMwhBwCVNgEbOl3QJY",
        type="JsonWebKey2020",
        did_controller="did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        public_key="0x0441ffbbe8f6fd93da9fad0114e96861801e87e1f5c53f617467a16a329c74f818226a24dbb1241422ab7faa764175fa710a57d5d52b33958efd37447e5826ea33",
        issecp256k1=True,
        notafter=datetime.now() + timedelta(days=365)
    )
    vmethod_rel_auth = VerificationRelationship(
        identifier_did="did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        name="authentication",
        vmethodid="did:ebsi:z95paQoBwGAqnnu4RKTmCtT#axZAOKbj-YyMiIN2CRLCwPjSCgMwhBwCVNgEbOl3QJY",
        notbefore=datetime.now(),
        notafter=datetime.now() + timedelta(days=365)
    )
    vmethod_rel_capability_invocation = VerificationRelationship(
        identifier_did="did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        name="capabilityInvocation",
        vmethodid="did:ebsi:z95paQoBwGAqnnu4RKTmCtT#axZAOKbj-YyMiIN2CRLCwPjSCgMwhBwCVNgEbOl3QJY",
        notbefore=datetime.now(),
        notafter=datetime.now() + timedelta(days=365)
    )
    session.add(identifier)
    session.add(vmethod)
    session.add(vmethod_rel_auth)
    session.add(vmethod_rel_capability_invocation)
    session.commit()


def test_create_vp_with_vmethod(client: TestClient, session: Session, default_data):
    """
    Tests the creation of a verifiable presentation with a VerificationMethod on Wallet Mock API
    """
    verifiable_credential = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDplYnNpOnpFOTcxb1Q5ZXN1S2RjSHNwS2RmQVhnI3BqeWlUeFBYQUxtbUg0L1pCeGdvVVNpYnB6ektDbnRNWGx6eVBHWXp1cEkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJkaWQ6ZWJzaTp6RTk3MW9UOWVzdUtkY0hzcEtkZkFYZyIsInN1YiI6ImRpZDplYnNpOno5NXBhUW9Cd0dBcW5udTRSS1RtQ3RUIiwiaWF0IjoxNzc2MDA4NTM0LCJuYmYiOjE3NzYwMDg1MzQsImV4cCI6MjA5MTM2ODUzNCwianRpIjoidXJuOnV1aWQ6MzU2ZDUzNGEtNDhlZS00ZDQxLWI2NWQtNjg1ZmEzOTEyNTA4IiwidmMiOnsiY29udGV4dCI6W10sImlkIjoidXJuOnV1aWQ6MzU2ZDUzNGEtNDhlZS00ZDQxLWI2NWQtNjg1ZmEzOTEyNTA4IiwidHlwZSI6WyJWZXJpZmlhYmxlQXV0aG9yaXNhdGlvblRvT25ib2FyZCJdLCJpc3N1YW5jZURhdGUiOiIyMDI2LTA0LTEyVDE3OjQyOjE0LjA3Mzk0NyIsInZhbGlkRnJvbSI6IjIwMjYtMDQtMTJUMTc6NDI6MTQuMDczOTQ3IiwidmFsaWRVbnRpbCI6IjIwMzYtMDQtMDlUMTc6NDI6MTQuMDczOTY1IiwiZXhwaXJhdGlvbkRhdGUiOiIyMDM2LTA0LTA5VDE3OjQyOjE0LjA3Mzk2NSIsImlzc3VlZCI6IjIwMjYtMDQtMTJUMTc6NDI6MTQuMDczOTQ3IiwiaXNzdWVyIjoiZGlkOmVic2k6ekU5NzFvVDllc3VLZGNIc3BLZGZBWGciLCJjcmVkZW50aWFsU3ViamVjdCI6eyJpZCI6ImRpZDplYnNpOno5NXBhUW9Cd0dBcW5udTRSS1RtQ3RUIn0sImNyZWRlbnRpYWxTY2hlbWEiOnsiaWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L3RydXN0ZWQtc2NoZW1hcy1yZWdpc3RyeS92Mi9zY2hlbWFzLzB4MjMwMzllNjM1NmVhNmI3MDNjZTY3MmU3Y2ZhYzBiNDI3NjViMTUwZjYzZGY3OGUyYmQxOGFlNzg1Nzg3ZjZhMiIsInR5cGUiOiJGdWxsSnNvblNjaGVtYVZhbGlkYXRvcjIwMjEifX19.zWwmedljbMvZ-SuhMeO2LVrktquPflduiRljgw4Ewopt-xy9FCHUbgT8Y6GZ_IZ8sh2OQPLjTy5Ayngou6cYIQ"
    response = client.get("/wallet-mock/create_vp", params={
        "vc_token": verifiable_credential,
        "did": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        "private_key": "0xd34781e8008e6a57946b43d97cb09ac066144f4d3c5f5de1567fa7269434a831",
        "verification_id": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT#axZAOKbj-YyMiIN2CRLCwPjSCgMwhBwCVNgEbOl3QJY"
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_access_token_tnt_authorise(client: TestClient, default_data):
    """
    Tests the access token request for the tnt_authorise scope on Authorisation API
    """
    verifiable_presentation = "eyJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCNheFpBT0tiai1ZeU1pSU4yQ1JMQ3dQalNDZ013aEJ3Q1ZOZ0ViT2wzUUpZIiwidHlwIjoiSldUIn0.eyJpc3MiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCIsImF1ZCI6ImRpZDplYnNpOnpFOTcxb1Q5ZXN1S2RjSHNwS2RmQVhnIiwic3ViIjoiZGlkOmVic2k6ejk1cGFRb0J3R0Fxbm51NFJLVG1DdFQiLCJpYXQiOjE3NzYwMTYwMTksIm5iZiI6MTc3NjAxNjAxOSwiZXhwIjoyMDkxMzc2MDE5LCJub25jZSI6InVybjp1dWlkOjkxN2NmYWZjLTEyZGUtNDZhOS04NThkLTZjOGI1Y2E5MGJkMCIsImp0aSI6InVybjp1dWlkOjkxN2NmYWZjLTEyZGUtNDZhOS04NThkLTZjOGI1Y2E5MGJkMCIsInZwIjp7ImNvbnRleHQiOltdLCJpZCI6InVybjp1dWlkOjkxN2NmYWZjLTEyZGUtNDZhOS04NThkLTZjOGI1Y2E5MGJkMCIsInR5cGUiOlsiVmVyaWZpYWJsZVByZXNlbnRhdGlvbiJdLCJob2xkZXIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCIsInZlcmlmaWFibGVDcmVkZW50aWFsIjpbImV5SmhiR2NpT2lKRlV6STFOaUlzSW10cFpDSTZJbVJwWkRwbFluTnBPbnBGT1RjeGIxUTVaWE4xUzJSalNITndTMlJtUVZobkkzQnFlV2xVZUZCWVFVeHRiVWcwTDFwQ2VHZHZWVk5wWW5CNmVrdERiblJOV0d4NmVWQkhXWHAxY0VraUxDSjBlWEFpT2lKS1YxUWlmUS5leUpwYzNNaU9pSmthV1E2WldKemFUcDZSVGszTVc5VU9XVnpkVXRrWTBoemNFdGtaa0ZZWnlJc0luTjFZaUk2SW1ScFpEcGxZbk5wT25vNU5YQmhVVzlDZDBkQmNXNXVkVFJTUzFSdFEzUlVJaXdpYVdGMElqb3hOemMyTURBNE5UTTBMQ0p1WW1ZaU9qRTNOell3TURnMU16UXNJbVY0Y0NJNk1qQTVNVE0yT0RVek5Dd2lhblJwSWpvaWRYSnVPblYxYVdRNk16VTJaRFV6TkdFdE5EaGxaUzAwWkRReExXSTJOV1F0TmpnMVptRXpPVEV5TlRBNElpd2lkbU1pT25zaVkyOXVkR1Y0ZENJNlcxMHNJbWxrSWpvaWRYSnVPblYxYVdRNk16VTJaRFV6TkdFdE5EaGxaUzAwWkRReExXSTJOV1F0TmpnMVptRXpPVEV5TlRBNElpd2lkSGx3WlNJNld5SldaWEpwWm1saFlteGxRWFYwYUc5eWFYTmhkR2x2YmxSdlQyNWliMkZ5WkNKZExDSnBjM04xWVc1alpVUmhkR1VpT2lJeU1ESTJMVEEwTFRFeVZERTNPalF5T2pFMExqQTNNemswTnlJc0luWmhiR2xrUm5KdmJTSTZJakl3TWpZdE1EUXRNVEpVTVRjNk5ESTZNVFF1TURjek9UUTNJaXdpZG1Gc2FXUlZiblJwYkNJNklqSXdNell0TURRdE1EbFVNVGM2TkRJNk1UUXVNRGN6T1RZMUlpd2laWGh3YVhKaGRHbHZia1JoZEdVaU9pSXlNRE0yTFRBMExUQTVWREUzT2pReU9qRTBMakEzTXprMk5TSXNJbWx6YzNWbFpDSTZJakl3TWpZdE1EUXRNVEpVTVRjNk5ESTZNVFF1TURjek9UUTNJaXdpYVhOemRXVnlJam9pWkdsa09tVmljMms2ZWtVNU56RnZWRGxsYzNWTFpHTkljM0JMWkdaQldHY2lMQ0pqY21Wa1pXNTBhV0ZzVTNWaWFtVmpkQ0k2ZXlKcFpDSTZJbVJwWkRwbFluTnBPbm81TlhCaFVXOUNkMGRCY1c1dWRUUlNTMVJ0UTNSVUluMHNJbU55WldSbGJuUnBZV3hUWTJobGJXRWlPbnNpYVdRaU9pSm9kSFJ3Y3pvdkwyRndhUzF3YVd4dmRDNWxZbk5wTG1WMUwzUnlkWE4wWldRdGMyTm9aVzFoY3kxeVpXZHBjM1J5ZVM5Mk1pOXpZMmhsYldGekx6QjRNak13TXpsbE5qTTFObVZoTm1JM01ETmpaVFkzTW1VM1kyWmhZekJpTkRJM05qVmlNVFV3WmpZelpHWTNPR1V5WW1ReE9HRmxOemcxTnpnM1pqWmhNaUlzSW5SNWNHVWlPaUpHZFd4c1NuTnZibE5qYUdWdFlWWmhiR2xrWVhSdmNqSXdNakVpZlgxOS56V3dtZWRsamJNdlotU3VoTWVPMkxWcmt0cXVQZmxkdWlSbGpndzRFd29wdC14eTlGQ0hVYmdUOFk2R1pfSVo4c2gyT1FQTGpUeTVBeW5nb3U2Y1lJUSJdfX0.nXHxbqOPSAHFSY5D5P3PKPqEdM62orqQA9PbmHV4zS18WYy2GPldwwG62hCkEUq2FV-UwF58N0pQGAINveUsRA"
    response = client.post("/authorisation/token", json={
        "grant_type": "vp_token",
        "presentation_submission": {
            "definition_id": "tnt_authorise_presentation",
            "descriptor_map": [
                {
                    "format": "jwt_vp",
                    "id": "tnt_authorise_credential",
                    "path": "$",
                    "path_nested": {
                        "format": "jwt_vc",
                        "id": "tnt_authorise_credential",
                        "path": "$.vp.verifiableCredential[0]"
                    }
                }
            ],
            "id": "ac9026c2-c3f5-4a26-b609-ec215cf97ba2"
        },
        "scope": "openid tnt_authorise",
        "vp_token": verifiable_presentation
    })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["scope"] == "openid tnt_authorise"
    assert response.json()["access_token"] is not None
    assert response.json()["id_token"] is not None


def test_tnt_authorise_did_create_transaction(client: TestClient, default_data):
    """
    Tests the creation of a transaction to authorise a DID to TNT API
    """
    access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IlJWVzJva3h6LXp6TnpBRUZLTl9lSWtRaXQ2WERDaUp0N2szaW5WaDlSV1EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L2F1dGhvcmlzYXRpb24vdjQiLCJleHAiOjE3NzYwMjMyNTksImlhdCI6MTc3NjAxNjA1OSwiaXNzIjoiaHR0cHM6Ly9hcGktcGlsb3QuZWJzaS5ldS9hdXRob3Jpc2F0aW9uL3Y0IiwianRpIjoiY2FkZjIyM2MtOTBkYS00YmZlLTg0NjgtNjA0MmVjMTJhNGJjIiwic2NwIjoib3BlbmlkIHRudF9hdXRob3Jpc2UiLCJzdWIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCJ9.i3HthWBgDJ9ay8pHCB1UvXpVQM1E0x8MiPoK10VYUIxLQXo6BSF2YcXFp5A_IREl84W7_0CyZtXchHkcYuon9A"
    response = client.post("/track-and-trace/jsonrpc",
                           headers={
                               "Authorization": f"Bearer {access_token}",
                           },
                           json={
                               "jsonrpc": "2.0",
                               "method": "authoriseDid",
                               "params": [
                                   {
                                       "from": "0xaB6415d6A931A84Dfc02FFD551C4876048c39A92",
                                       "senderDid": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
                                       "authorisedDid": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
                                       "whiteList": "0x01"
                                   }
                               ],
                               "id": 474
                           })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["result"] is not None


def test_tnt_authorise_send_signed_transaction(client: TestClient, session: Session, default_data):
    """
    Tests the sending of an authoriseDid signed transaction to TNT API
    """
    access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IlJWVzJva3h6LXp6TnpBRUZLTl9lSWtRaXQ2WERDaUp0N2szaW5WaDlSV1EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L2F1dGhvcmlzYXRpb24vdjQiLCJleHAiOjE3NzYwMjMyNTksImlhdCI6MTc3NjAxNjA1OSwiaXNzIjoiaHR0cHM6Ly9hcGktcGlsb3QuZWJzaS5ldS9hdXRob3Jpc2F0aW9uL3Y0IiwianRpIjoiY2FkZjIyM2MtOTBkYS00YmZlLTg0NjgtNjA0MmVjMTJhNGJjIiwic2NwIjoib3BlbmlkIHRudF9hdXRob3Jpc2UiLCJzdWIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCJ9.i3HthWBgDJ9ay8pHCB1UvXpVQM1E0x8MiPoK10VYUIxLQXo6BSF2YcXFp5A_IREl84W7_0CyZtXchHkcYuon9A"
    signed_transaction = {
        "protocol": "eth",
        "unsignedTransaction": {
            "value": 0,
            "from": "0xaB6415d6A931A84Dfc02FFD551C4876048c39A92",
            "to": "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05",
            "nonce": 45523,
            "chainId": 1234,
            "gas": 0,
            "gasPrice": 0,
            "data": "0xff421956000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d43745400000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d437454"
        },
        "r": "0xd2c5b3c7c395095ad2ec3df5ec03819752b39b9279b512273f3758b6dced4e2e",
        "s": "0x546744019c1bd14931799b6eb4566658c99a35fa78de4fad26bc93a3c7b3dcdb",
        "v": 2504,
        "signedRawTransaction": "f9014682b1d3808094823bbc0cee3de3b61acfa0ceedb951ab9a013f0580b8e4ff421956000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d43745400000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d4374548209c8a0d2c5b3c7c395095ad2ec3df5ec03819752b39b9279b512273f3758b6dced4e2ea0546744019c1bd14931799b6eb4566658c99a35fa78de4fad26bc93a3c7b3dcdb"
    }

    response = client.post("/track-and-trace/jsonrpc",
                           headers={
                               "Authorization": f"Bearer {access_token}",
                           },
                           json={
                               "jsonrpc": "2.0",
                               "method": "sendSignedTransaction",
                               "id": 1,
                               "params": [
                                   signed_transaction
                               ]
                           })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["result"] is not None

    identifier = session.get(Identifier, "did:ebsi:z95paQoBwGAqnnu4RKTmCtT")
    assert identifier is not None
    assert identifier.tnt_authorized == True
