from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from ebsi_sim.src.models.didr import Identifier, VerificationMethod, VerificationRelationship
from ebsi_sim.src.models.tnt import Document


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
        tnt_authorized=True
    )
    vmethod = VerificationMethod(
        id="did:ebsi:z95paQoBwGAqnnu4RKTmCtT#axZAOKbj-YyMiIN2CRLCwPjSCgMwhBwCVNgEbOl3QJY",
        type="JsonWebKey2020",
        did_controller="did:ebsi:z95paQoBwGAqnnu4RKTmCtT",
        public_key="0x04625f44f6ef03abcc854a95d2104dc8230da8ce15180a20d218aeb45a9ecaa2a68aab4d69ec2e10be1f04010c3c62108cdb3d20abefc15d59233c81b17b69f734",
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


def test_access_token_tnt_create(client: TestClient, default_data):
    """
    Tests the access token request for the tnt_create scope on Authorisation API
    """
    verifiable_presentation = "eyJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCNheFpBT0tiai1ZeU1pSU4yQ1JMQ3dQalNDZ013aEJ3Q1ZOZ0ViT2wzUUpZIiwidHlwIjoiSldUIn0.eyJpc3MiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCIsImF1ZCI6ImRpZDplYnNpOnpFOTcxb1Q5ZXN1S2RjSHNwS2RmQVhnIiwic3ViIjoiZGlkOmVic2k6ejk1cGFRb0J3R0Fxbm51NFJLVG1DdFQiLCJpYXQiOjE3Nzc1NjI0NzgsIm5iZiI6MTc3NzU2MjQ3OCwiZXhwIjoyMDkyOTIyNDc4LCJub25jZSI6InVybjp1dWlkOjkzMDU0MTE1LWU3ZDYtNGViNi04ZjJlLThjMDRhY2EzYjVmMCIsImp0aSI6InVybjp1dWlkOjkzMDU0MTE1LWU3ZDYtNGViNi04ZjJlLThjMDRhY2EzYjVmMCIsInZwIjp7ImNvbnRleHQiOltdLCJpZCI6InVybjp1dWlkOjkzMDU0MTE1LWU3ZDYtNGViNi04ZjJlLThjMDRhY2EzYjVmMCIsInR5cGUiOlsiVmVyaWZpYWJsZVByZXNlbnRhdGlvbiJdLCJob2xkZXIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCIsInZlcmlmaWFibGVDcmVkZW50aWFsIjpbImV5SmhiR2NpT2lKRlV6STFOaUlzSW10cFpDSTZJbVJwWkRwbFluTnBPbnBGT1RjeGIxUTVaWE4xUzJSalNITndTMlJtUVZobkkzQnFlV2xVZUZCWVFVeHRiVWcwTDFwQ2VHZHZWVk5wWW5CNmVrdERiblJOV0d4NmVWQkhXWHAxY0VraUxDSjBlWEFpT2lKS1YxUWlmUS5leUpwYzNNaU9pSmthV1E2WldKemFUcDZSVGszTVc5VU9XVnpkVXRrWTBoemNFdGtaa0ZZWnlJc0luTjFZaUk2SW1ScFpEcGxZbk5wT25vNU5YQmhVVzlDZDBkQmNXNXVkVFJTUzFSdFEzUlVJaXdpYVdGMElqb3hOemMyTURBNE5UTTBMQ0p1WW1ZaU9qRTNOell3TURnMU16UXNJbVY0Y0NJNk1qQTVNVE0yT0RVek5Dd2lhblJwSWpvaWRYSnVPblYxYVdRNk16VTJaRFV6TkdFdE5EaGxaUzAwWkRReExXSTJOV1F0TmpnMVptRXpPVEV5TlRBNElpd2lkbU1pT25zaVkyOXVkR1Y0ZENJNlcxMHNJbWxrSWpvaWRYSnVPblYxYVdRNk16VTJaRFV6TkdFdE5EaGxaUzAwWkRReExXSTJOV1F0TmpnMVptRXpPVEV5TlRBNElpd2lkSGx3WlNJNld5SldaWEpwWm1saFlteGxRWFYwYUc5eWFYTmhkR2x2YmxSdlQyNWliMkZ5WkNKZExDSnBjM04xWVc1alpVUmhkR1VpT2lJeU1ESTJMVEEwTFRFeVZERTNPalF5T2pFMExqQTNNemswTnlJc0luWmhiR2xrUm5KdmJTSTZJakl3TWpZdE1EUXRNVEpVTVRjNk5ESTZNVFF1TURjek9UUTNJaXdpZG1Gc2FXUlZiblJwYkNJNklqSXdNell0TURRdE1EbFVNVGM2TkRJNk1UUXVNRGN6T1RZMUlpd2laWGh3YVhKaGRHbHZia1JoZEdVaU9pSXlNRE0yTFRBMExUQTVWREUzT2pReU9qRTBMakEzTXprMk5TSXNJbWx6YzNWbFpDSTZJakl3TWpZdE1EUXRNVEpVTVRjNk5ESTZNVFF1TURjek9UUTNJaXdpYVhOemRXVnlJam9pWkdsa09tVmljMms2ZWtVNU56RnZWRGxsYzNWTFpHTkljM0JMWkdaQldHY2lMQ0pqY21Wa1pXNTBhV0ZzVTNWaWFtVmpkQ0k2ZXlKcFpDSTZJbVJwWkRwbFluTnBPbm81TlhCaFVXOUNkMGRCY1c1dWRUUlNTMVJ0UTNSVUluMHNJbU55WldSbGJuUnBZV3hUWTJobGJXRWlPbnNpYVdRaU9pSm9kSFJ3Y3pvdkwyRndhUzF3YVd4dmRDNWxZbk5wTG1WMUwzUnlkWE4wWldRdGMyTm9aVzFoY3kxeVpXZHBjM1J5ZVM5Mk1pOXpZMmhsYldGekx6QjRNak13TXpsbE5qTTFObVZoTm1JM01ETmpaVFkzTW1VM1kyWmhZekJpTkRJM05qVmlNVFV3WmpZelpHWTNPR1V5WW1ReE9HRmxOemcxTnpnM1pqWmhNaUlzSW5SNWNHVWlPaUpHZFd4c1NuTnZibE5qYUdWdFlWWmhiR2xrWVhSdmNqSXdNakVpZlgxOS56V3dtZWRsamJNdlotU3VoTWVPMkxWcmt0cXVQZmxkdWlSbGpndzRFd29wdC14eTlGQ0hVYmdUOFk2R1pfSVo4c2gyT1FQTGpUeTVBeW5nb3U2Y1lJUSJdfX0.Mas2i2PzZrgsRvXbUyDLYIIu_84442EcqC2NnuSc2nuUWMHyhd_nHgp2pXjJVtwF0duqd3wA7Frwb5oAC29-NQ"
    response = client.post("/authorisation/token", json={
        "grant_type": "vp_token",
        "presentation_submission": {
            "definition_id": "tnt_create_presentation",
            "descriptor_map": [],
            "id": "ac9026c2-c3f5-4a26-b609-ec215cf97ba2"
        },
        "scope": "openid tnt_create",
        "vp_token": verifiable_presentation
    })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["scope"] == "openid tnt_create"
    assert response.json()["access_token"] is not None
    assert response.json()["id_token"] is not None


def test_tnt_document_create_transaction(client: TestClient, default_data):
    """
    Tests the creation of a transaction to create a TNT Document on TNT API
    """
    access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IlJWVzJva3h6LXp6TnpBRUZLTl9lSWtRaXQ2WERDaUp0N2szaW5WaDlSV1EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L2F1dGhvcmlzYXRpb24vdjQiLCJleHAiOjE3NzYxMjMzODYsImlhdCI6MTc3NjExNjE4NiwiaXNzIjoiaHR0cHM6Ly9hcGktcGlsb3QuZWJzaS5ldS9hdXRob3Jpc2F0aW9uL3Y0IiwianRpIjoiYjRjOWNmNTgtNDU0OS00ZjhiLTk3YzQtM2U1MWJhODgxZWQxIiwic2NwIjoib3BlbmlkIHRudF9jcmVhdGUiLCJzdWIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCJ9.j2TFKMyPwheXqYD3sVUlXOAXjfg1odc1FATiDvn7XuEo0aw6DsCeJaWFO2_y8fGT5qwEYAl2P9FGvHDKKBwn7w"
    response = client.post("/track-and-trace/jsonrpc",
                           headers={
                               "Authorization": f"Bearer {access_token}",
                           },
                           json={
                               "jsonrpc": "2.0",
                               "method": "createDocument",
                               "params": [
                                   {
                                       "from": "0xaB6415d6A931A84Dfc02FFD551C4876048c39A92",
                                       "documentHash": "0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
                                       "documentMetadata": "0x74657374206d65746164617461",
                                       "didEbsiCreator": "did:ebsi:z95paQoBwGAqnnu4RKTmCtT"
                                   }
                               ],
                               "id": 474
                           })
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["result"] is not None


def test_tnt_document_send_signed_transaction(client: TestClient, session: Session, default_data):
    """
    Tests the sending of an createDocument signed transaction to TNT API
    """
    access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IlJWVzJva3h6LXp6TnpBRUZLTl9lSWtRaXQ2WERDaUp0N2szaW5WaDlSV1EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJodHRwczovL2FwaS1waWxvdC5lYnNpLmV1L2F1dGhvcmlzYXRpb24vdjQiLCJleHAiOjE3NzYxMjMzODYsImlhdCI6MTc3NjExNjE4NiwiaXNzIjoiaHR0cHM6Ly9hcGktcGlsb3QuZWJzaS5ldS9hdXRob3Jpc2F0aW9uL3Y0IiwianRpIjoiYjRjOWNmNTgtNDU0OS00ZjhiLTk3YzQtM2U1MWJhODgxZWQxIiwic2NwIjoib3BlbmlkIHRudF9jcmVhdGUiLCJzdWIiOiJkaWQ6ZWJzaTp6OTVwYVFvQndHQXFubnU0UktUbUN0VCJ9.j2TFKMyPwheXqYD3sVUlXOAXjfg1odc1FATiDvn7XuEo0aw6DsCeJaWFO2_y8fGT5qwEYAl2P9FGvHDKKBwn7w"
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
            "data": "0xda62b06bcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000001c307837343635373337343230366436353734363136343631373436310000000000000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d437454"
        },
        "r": "0x12d1e1d0c3bb88c6264e27c503e04e71887606f1597d30697b923b19381dffb2",
        "s": "0x52d2a3b9718750546abf7fe4e1fe8b0137f14ce73d8fea2c481ff7718ed9fa08",
        "v": 2503,
        "signedRawTransaction": "f9014682b1d3808094823bbc0cee3de3b61acfa0ceedb951ab9a013f0580b8e4da62b06bcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000001c307837343635373337343230366436353734363136343631373436310000000000000000000000000000000000000000000000000000000000000000000000206469643a656273693a7a39357061516f42774741716e6e7534524b546d4374548209c7a012d1e1d0c3bb88c6264e27c503e04e71887606f1597d30697b923b19381dffb2a052d2a3b9718750546abf7fe4e1fe8b0137f14ce73d8fea2c481ff7718ed9fa08"
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

    tnt_document = session.get(Document, "0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67")
    assert tnt_document is not None
