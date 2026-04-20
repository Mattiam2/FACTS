import json

from fastapi.testclient import TestClient
from sqlmodel import Session

from ebsi_sim.models.didr import Identifier


def test_request_vc(client: TestClient):
    response = client.get("/issuer-mock/request_vc", params={
        "subject_did": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        "credential_type": "VerifiableAuthorisationToOnboard"
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_create_vp(client: TestClient):
    verifiable_credential = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDplYnNpOnpFOTcxb1Q5ZXN1S2RjSHNwS2RmQVhnI3BqeWlUeFBYQUxtbUg0L1pCeGdvVVNpYnB6ektDbnRNWGx6eVBHWXp1cEkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJkaWQ6ZWJzaTp6RTk3MW9UOWVzdUtkY0hzcEtkZkFYZyIsInN1YiI6ImRpZDplYnNpOno5NXBhUW9Cd0dBcW5udTRSS1RtQ3RUIiwiaWF0IjoxNzc2MDA4NTM0LCJuYmYiOjE3NzYwMDg1MzQsImV4cCI6MjA5MTM2ODUzNCwianRpIjoidXJuOnV1aWQ6MzU2ZDUzNGEtNDhlZS00ZDQxLWI2NWQtNjg1ZmEzOTEyNTA4IiwidmMiOnsiY29udGV4dCI6W10sImlkIjoidXJuOnV1aWQ6MzU2ZDUzNGEtNDhlZS00ZDQxLWI2NWQtNjg1ZmEzOTEyNTA4IiwidHlwZSI6WyJWZXJpZmlhYmxlQXV0aG9yaXNhdGlvblRvT25ib2FyZCJdLCJpc3N1YW5jZURhdGUiOiIyMDI2LTA0LTEyVDE3OjQyOjE0LjA3Mzk0NyIsInZhbGlkRnJvbSI6IjIwMjYtMDQtMTJUMTc6NDI6MTQuMDczOTQ3IiwidmFsaWRVbnRpbCI6IjIwMzYtMDQtMDlUMTc6NDI6MTQuMDczOTY1IiwiZXhwaXJhdGlvbkRhdGUiOiIyMDM2LTA0LTA5VDE3OjQyOjE0LjA3Mzk2NSIsImlzc3VlZCI6IjIwMjYtMDQtMTJUMTc6NDI6MTQuMDczOTQ3IiwiaXNzdWVyIjoiZGlkOmVic2k6ekU5NzFvVDllc3VLZGNIc3BLZGZBWGciLCJjcmVkZW50aWFsU3ViamVjdCI6eyJpZCI6ImRpZDplYnNpOno5NXBhUW9Cd0dBcW5udTRSS1RtQ3RUIn0sImNyZWRlbnRpYWxTY2hlbWEiOnsiaWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L3RydXN0ZWQtc2NoZW1hcy1yZWdpc3RyeS92Mi9zY2hlbWFzLzB4MjMwMzllNjM1NmVhNmI3MDNjZTY3MmU3Y2ZhYzBiNDI3NjViMTUwZjYzZGY3OGUyYmQxOGFlNzg1Nzg3ZjZhMiIsInR5cGUiOiJGdWxsSnNvblNjaGVtYVZhbGlkYXRvcjIwMjEifX19.zWwmedljbMvZ-SuhMeO2LVrktquPflduiRljgw4Ewopt-xy9FCHUbgT8Y6GZ_IZ8sh2OQPLjTy5Ayngou6cYIQ"
    response = client.get("/wallet-mock/create_vp", params={
        "vc_token": verifiable_credential,
        "did": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        "private_key": "0xd34781e8008e6a57946b43d97cb09ac066144f4d3c5f5de1567fa7269434a831"
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_access_token_didr_invite(client: TestClient):
    verifiable_presentation = "eyJhbGciOiJFUzI1NksiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCIsImF1ZCI6ImRpZDplYnNpOnpFOTcxb1Q5ZXN1S2RjSHNwS2RmQVhnIiwic3ViIjoiZGlkOmVic2k6ejk1cGFRb0J3R0Fxbm51NFJLVG1DdFQiLCJpYXQiOjE3NzYwMDk3MzQsIm5iZiI6MTc3NjAwOTczNCwiZXhwIjoyMDkxMzY5NzM0LCJub25jZSI6InVybjp1dWlkOmUzYmI4YjlhLTYyNTgtNGZkOC1hZTI2LTE3ZTA0MTJjMDBhOSIsImp0aSI6InVybjp1dWlkOmUzYmI4YjlhLTYyNTgtNGZkOC1hZTI2LTE3ZTA0MTJjMDBhOSIsInZwIjp7ImNvbnRleHQiOltdLCJpZCI6InVybjp1dWlkOmUzYmI4YjlhLTYyNTgtNGZkOC1hZTI2LTE3ZTA0MTJjMDBhOSIsInR5cGUiOlsiVmVyaWZpYWJsZVByZXNlbnRhdGlvbiJdLCJob2xkZXIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCIsInZlcmlmaWFibGVDcmVkZW50aWFsIjpbImV5SmhiR2NpT2lKRlV6STFOaUlzSW10cFpDSTZJbVJwWkRwbFluTnBPbnBGT1RjeGIxUTVaWE4xUzJSalNITndTMlJtUVZobkkzQnFlV2xVZUZCWVFVeHRiVWcwTDFwQ2VHZHZWVk5wWW5CNmVrdERiblJOV0d4NmVWQkhXWHAxY0VraUxDSjBlWEFpT2lKS1YxUWlmUS5leUpwYzNNaU9pSmthV1E2WldKemFUcDZSVGszTVc5VU9XVnpkVXRrWTBoemNFdGtaa0ZZWnlJc0luTjFZaUk2SW1ScFpEcGxZbk5wT25vNU5YQmhVVzlDZDBkQmNXNXVkVFJTUzFSdFEzUlVJaXdpYVdGMElqb3hOemMyTURBNE5UTTBMQ0p1WW1ZaU9qRTNOell3TURnMU16UXNJbVY0Y0NJNk1qQTVNVE0yT0RVek5Dd2lhblJwSWpvaWRYSnVPblYxYVdRNk16VTJaRFV6TkdFdE5EaGxaUzAwWkRReExXSTJOV1F0TmpnMVptRXpPVEV5TlRBNElpd2lkbU1pT25zaVkyOXVkR1Y0ZENJNlcxMHNJbWxrSWpvaWRYSnVPblYxYVdRNk16VTJaRFV6TkdFdE5EaGxaUzAwWkRReExXSTJOV1F0TmpnMVptRXpPVEV5TlRBNElpd2lkSGx3WlNJNld5SldaWEpwWm1saFlteGxRWFYwYUc5eWFYTmhkR2x2YmxSdlQyNWliMkZ5WkNKZExDSnBjM04xWVc1alpVUmhkR1VpT2lJeU1ESTJMVEEwTFRFeVZERTNPalF5T2pFMExqQTNNemswTnlJc0luWmhiR2xrUm5KdmJTSTZJakl3TWpZdE1EUXRNVEpVTVRjNk5ESTZNVFF1TURjek9UUTNJaXdpZG1Gc2FXUlZiblJwYkNJNklqSXdNell0TURRdE1EbFVNVGM2TkRJNk1UUXVNRGN6T1RZMUlpd2laWGh3YVhKaGRHbHZia1JoZEdVaU9pSXlNRE0yTFRBMExUQTVWREUzT2pReU9qRTBMakEzTXprMk5TSXNJbWx6YzNWbFpDSTZJakl3TWpZdE1EUXRNVEpVTVRjNk5ESTZNVFF1TURjek9UUTNJaXdpYVhOemRXVnlJam9pWkdsa09tVmljMms2ZWtVNU56RnZWRGxsYzNWTFpHTkljM0JMWkdaQldHY2lMQ0pqY21Wa1pXNTBhV0ZzVTNWaWFtVmpkQ0k2ZXlKcFpDSTZJbVJwWkRwbFluTnBPbm81TlhCaFVXOUNkMGRCY1c1dWRUUlNTMVJ0UTNSVUluMHNJbU55WldSbGJuUnBZV3hUWTJobGJXRWlPbnNpYVdRaU9pSm9kSFJ3Y3pvdkwyRndhUzF3YVd4dmRDNWxZbk5wTG1WMUwzUnlkWE4wWldRdGMyTm9aVzFoY3kxeVpXZHBjM1J5ZVM5Mk1pOXpZMmhsYldGekx6QjRNak13TXpsbE5qTTFObVZoTm1JM01ETmpaVFkzTW1VM1kyWmhZekJpTkRJM05qVmlNVFV3WmpZelpHWTNPR1V5WW1ReE9HRmxOemcxTnpnM1pqWmhNaUlzSW5SNWNHVWlPaUpHZFd4c1NuTnZibE5qYUdWdFlWWmhiR2xrWVhSdmNqSXdNakVpZlgxOS56V3dtZWRsamJNdlotU3VoTWVPMkxWcmt0cXVQZmxkdWlSbGpndzRFd29wdC14eTlGQ0hVYmdUOFk2R1pfSVo4c2gyT1FQTGpUeTVBeW5nb3U2Y1lJUSJdfX0.g9cbRxiQCef6yFdqGbxgnVnunvPbfUhKjmFaxiUqTkOgPOt-8BXMgShx7iVoSpg-meq7kUXJg-kd6kFQaAfj-w"
    response = client.post("/authorisation/token", json={
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
            "id": "ac9026c2-c3f5-4a26-b609-ec215cf97ba2"
        },
        "scope": "openid didr_invite",
        "vp_token": verifiable_presentation
    })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["scope"] == "openid didr_invite"
    assert response.json()["access_token"] is not None
    assert response.json()["id_token"] is not None


def test_insert_did_document_create_transaction(client: TestClient):
    access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IlJWVzJva3h6LXp6TnpBRUZLTl9lSWtRaXQ2WERDaUp0N2szaW5WaDlSV1EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L2F1dGhvcmlzYXRpb24vdjQiLCJleHAiOjE3NzYwMTgyODEsImlhdCI6MTc3NjAxMTA4MSwiaXNzIjoiaHR0cHM6Ly9hcGktcGlsb3QuZWJzaS5ldS9hdXRob3Jpc2F0aW9uL3Y0IiwianRpIjoiNzJjYTIxZWEtMjc0Ny00OGY3LThhMzAtMGY1NTY4ZmU4MDJjIiwic2NwIjoib3BlbmlkIGRpZHJfaW52aXRlIiwic3ViIjoiZGlkOmVic2k6ejk1cGFRb0J3R0Fxbm51NFJLVG1DdFQifQ.v_Agb9amSvFbxhumlS8nJk9gTo0s_2WZruAcaq274dX8icHyL90175UoRVV9yOgvmu2rUavvAlw-i4j1jv7OAA"
    response = client.post("/did-registry/jsonrpc",
                           headers={
                               "Authorization": f"Bearer {access_token}",
                           },
                           json={
                               "jsonrpc": "2.0",
                               "method": "insertDidDocument",
                               "params": [
                                   {
                                       "from": "0xaB6415d6A931A84Dfc02FFD551C4876048c39A92",
                                       "did": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
                                       "baseDocument": "{\"@context\":[\"https://www.w3.org/ns/did/v1\",\"https://w3id.org/security/suites/jws-2020/v1\"]}",
                                       "vMethodId": "axZAOKbj-YyMiIN2CRLCwPjSCgMwhBwCVNgEbOl3QJY",
                                       "publicKey": "0x0441ffbbe8f6fd93da9fad0114e96861801e87e1f5c53f617467a16a329c74f818226a24dbb1241422ab7faa764175fa710a57d5d52b33958efd37447e5826ea33",
                                       "isSecp256k1": True,
                                       "notBefore": 1774707573,
                                       "notAfter": 2090326773
                                   }
                               ],
                               "id": 474
                           })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["result"] is not None


def test_insert_did_document_sign_transaction(client: TestClient):
    transaction_data = json.dumps({
        "value": 0,
        "from": "0xaB6415d6A931A84Dfc02FFD551C4876048c39A92",
        "to": "0x823BBc0ceE3dE3B61AcfA0CEedb951AB9a013F05",
        "nonce": 45523,
        "chainId": 1234,
        "gas": 0,
        "gasPrice": 0,
        "data": "0xfbb2240800000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000069c7e375000000000000000000000000000000000000000000000000000000007c97daf500000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d437454000000000000000000000000000000000000000000000000000000000000005c7b2240636f6e74657874223a5b2268747470733a2f2f7777772e77332e6f72672f6e732f6469642f7631222c2268747470733a2f2f773369642e6f72672f73656375726974792f7375697465732f6a77732d323032302f7631225d7d00000000000000000000000000000000000000000000000000000000000000000000002b61785a414f4b626a2d59794d69494e3243524c4377506a5343674d7768427743564e6745624f6c33514a5900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000410441ffbbe8f6fd93da9fad0114e96861801e87e1f5c53f617467a16a329c74f818226a24dbb1241422ab7faa764175fa710a57d5d52b33958efd37447e5826ea3300000000000000000000000000000000000000000000000000000000000000"
    })

    response = client.get("/wallet-mock/sign_transaction",
                          params={
                              "transaction": transaction_data,
                              "private_key": "0x0a30a737e618bd00bfc0113f2a26bbf14c0b9dc5697de8e9ef65e9b7310ae8f7"
                          })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["unsignedTransaction"] is not None
    assert response.json()["signedRawTransaction"] is not None


def test_insert_did_document_send_signed_transaction(client: TestClient, session: Session):
    access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IlJWVzJva3h6LXp6TnpBRUZLTl9lSWtRaXQ2WERDaUp0N2szaW5WaDlSV1EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L2F1dGhvcmlzYXRpb24vdjQiLCJleHAiOjE3NzYwMTgyODEsImlhdCI6MTc3NjAxMTA4MSwiaXNzIjoiaHR0cHM6Ly9hcGktcGlsb3QuZWJzaS5ldS9hdXRob3Jpc2F0aW9uL3Y0IiwianRpIjoiNzJjYTIxZWEtMjc0Ny00OGY3LThhMzAtMGY1NTY4ZmU4MDJjIiwic2NwIjoib3BlbmlkIGRpZHJfaW52aXRlIiwic3ViIjoiZGlkOmVic2k6ejk1cGFRb0J3R0Fxbm51NFJLVG1DdFQifQ.v_Agb9amSvFbxhumlS8nJk9gTo0s_2WZruAcaq274dX8icHyL90175UoRVV9yOgvmu2rUavvAlw-i4j1jv7OAA"
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
            "data": "0xfbb2240800000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000069c7e375000000000000000000000000000000000000000000000000000000007c97daf500000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d437454000000000000000000000000000000000000000000000000000000000000005c7b2240636f6e74657874223a5b2268747470733a2f2f7777772e77332e6f72672f6e732f6469642f7631222c2268747470733a2f2f773369642e6f72672f73656375726974792f7375697465732f6a77732d323032302f7631225d7d00000000000000000000000000000000000000000000000000000000000000000000002b61785a414f4b626a2d59794d69494e3243524c4377506a5343674d7768427743564e6745624f6c33514a5900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000410441ffbbe8f6fd93da9fad0114e96861801e87e1f5c53f617467a16a329c74f818226a24dbb1241422ab7faa764175fa710a57d5d52b33958efd37447e5826ea3300000000000000000000000000000000000000000000000000000000000000"
        },
        "r": "0x8a85abf33ae2e13c4bba3893b86dcf38d9e6554bffe250117663bf2a8e5d8c34",
        "s": "0x41bf074c201999b898a66500c6305c0b0b990bea06f07f39a889386c7e8540d4",
        "v": 2504,
        "signedRawTransaction": "f902e782b1d3808094823bbc0cee3de3b61acfa0ceedb951ab9a013f0580b90284fbb2240800000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000069c7e375000000000000000000000000000000000000000000000000000000007c97daf500000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d437454000000000000000000000000000000000000000000000000000000000000005c7b2240636f6e74657874223a5b2268747470733a2f2f7777772e77332e6f72672f6e732f6469642f7631222c2268747470733a2f2f773369642e6f72672f73656375726974792f7375697465732f6a77732d323032302f7631225d7d00000000000000000000000000000000000000000000000000000000000000000000002b61785a414f4b626a2d59794d69494e3243524c4377506a5343674d7768427743564e6745624f6c33514a5900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000410441ffbbe8f6fd93da9fad0114e96861801e87e1f5c53f617467a16a329c74f818226a24dbb1241422ab7faa764175fa710a57d5d52b33958efd37447e5826ea33000000000000000000000000000000000000000000000000000000000000008209c8a08a85abf33ae2e13c4bba3893b86dcf38d9e6554bffe250117663bf2a8e5d8c34a041bf074c201999b898a66500c6305c0b0b990bea06f07f39a889386c7e8540d4"
    }

    response = client.post("/did-registry/jsonrpc",
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

    added_did = session.get(Identifier, "did:ebsi:z95paQoBwGAqnnu4RKTmCtT")
    assert added_did is not None
