def test_read_abi(client):
    response = client.get("/did-registry/abi")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_identifiers(client):
    response = client.get("/did-registry/identifiers")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_identifier(client):
    response = client.get("/did-registry/identifiers/did:ebsi:zE971oT9esuKdcHspKdfAXg")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_identifier_not_found(client):
    response = client.get("/did-registry/identifiers/did:fake")
    assert response.status_code == 404
