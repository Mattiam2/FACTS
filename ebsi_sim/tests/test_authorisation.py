from fastapi.testclient import TestClient

def test_read_oidc_config(client: TestClient):
    """
    Tests the retrieval of the OpenID Connect configuration via the designated endpoint.
    """
    response = client.get("/authorisation/.well-known/openid-configuration")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tir_write(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tir_write`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tir_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tnt_write(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tnt_write`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tnt_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tpr_write(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tpr_write`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tpr_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_didr_invite(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `didr_invite`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid didr_invite',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_didr_write(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `didr_write`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid didr_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_timestamp_write(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `timestamp_write`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid timestamp_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tir_invite(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tir_invite`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tir_invite',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tnt_authorise(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tnt_authorise`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tnt_authorise',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tnt_create(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tnt_create`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tnt_create',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_tsr_write(client: TestClient):
    """
    Tests the retrieval of presentation definitions specific to the `tsr_write`
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tsr_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_presentation_definitions_fake(client: TestClient):
    """
    Tests the retrieval of presentation definitions with a non-existing
    scope using the provided test client.
    """
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'fake',
    })
    assert response.status_code == 422
