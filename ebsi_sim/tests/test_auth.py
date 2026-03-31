from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_read_oidc_config():
    response = client.get("/authorisation/.well-known/openid-configuration")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tir_write():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tir_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tnt_write():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tnt_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tpr_write():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tpr_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_didr_invite():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid didr_invite',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_didr_write():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid didr_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_timestamp_write():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid timestamp_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tir_invite():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tir_invite',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tnt_authorise():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tnt_authorise',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tnt_create():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tnt_create',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_tsr_write():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'openid tsr_write',
    })
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_presentation_definitions_fake():
    response = client.get("/authorisation/presentation-definitions", params={
        "scope": 'fake',
    })
    assert response.status_code == 422

