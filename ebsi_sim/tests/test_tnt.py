def test_read_abi(client):
    response = client.get("/track-and-trace/abi")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_head_accesses(client):
    response = client.head("/track-and-trace/accesses", params={
        "creator": 'did:ebsi:zE971oT9esuKdcHspKdfAXg',
    })
    assert response.status_code == 204


def test_head_accesses_not_found(client):
    response = client.head("/track-and-trace/accesses", params={
        "creator": 'did:fake',
    })
    assert response.status_code == 404


def test_read_accesses(client):
    response = client.get("/track-and-trace/accesses", params={
        "subject": "did:ebsi:zE971oT9esuKdcHspKdfAXg"
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_documents(client):
    response = client.get("/track-and-trace/documents")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document(client):
    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_not_found(client):
    response = client.get("/track-and-trace/documents/fake")
    assert response.status_code == 404
    assert len(response.json()) > 0


def test_read_document_events(client):
    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/events")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_not_found_events(client):
    response = client.get("/track-and-trace/documents/fake/events")
    assert response.status_code == 404


def test_read_document_event(client):
    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/events/0x02a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_event_not_found(client):
    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/events/fake")
    assert response.status_code == 404


def test_read_document_accesses(client):
    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/accesses")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_not_found_accesses(client):
    response = client.get("/track-and-trace/documents/fake/accesses")
    assert response.status_code == 404
    assert len(response.json()) > 0
