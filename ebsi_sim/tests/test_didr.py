from fastapi.testclient import TestClient

def test_read_abi(client: TestClient):
    """
    Tests the retrieval of the DID Registry ABI.
    """
    response = client.get("/did-registry/abi")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_identifiers(client: TestClient):
    """
    Tests the retrieval of all identifiers.
    """
    response = client.get("/did-registry/identifiers")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_identifier(client: TestClient):
    """
    Tests the retrieval of a specific identifier.
    """
    response = client.get("/did-registry/identifiers/did:ebsi:zE971oT9esuKdcHspKdfAXg")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_identifier_not_found(client: TestClient):
    """
    Tests the retrieval of a non-existent identifier.
    """
    response = client.get("/did-registry/identifiers/did:fake")
    assert response.status_code == 404
