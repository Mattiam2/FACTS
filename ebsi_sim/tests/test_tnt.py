from fastapi.testclient import TestClient
from ebsi_sim.models.tnt import Document, Event, Access

def test_read_abi(client: TestClient):
    response = client.get("/track-and-trace/abi")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_head_accesses(client: TestClient):
    response = client.head("/track-and-trace/accesses", params={
        "creator": 'did:ebsi:zE971oT9esuKdcHspKdfAXg',
    })
    assert response.status_code == 204


def test_head_accesses_not_found(client: TestClient):
    response = client.head("/track-and-trace/accesses", params={
        "creator": 'did:fake',
    })
    assert response.status_code == 404


def test_read_accesses(client: TestClient):
    response = client.get("/track-and-trace/accesses", params={
        "subject": "did:ebsi:zE971oT9esuKdcHspKdfAXg"
    })
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_documents(client: TestClient):
    response = client.get("/track-and-trace/documents")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document(client, session):
    d = Document(
        id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="This is a test document",
        timestamp_source="block",
        creator="did:ebsi:zE971oT9esuKdcHspKdfAXg",
    )
    session.add(d)
    session.commit()

    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_not_found(client: TestClient):
    response = client.get("/track-and-trace/documents/fake")
    assert response.status_code == 404
    assert len(response.json()) > 0


def test_read_document_events(client, session):
    d = Document(
        id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="This is a test document",
        timestamp_source="block",
        creator="did:ebsi:zE971oT9esuKdcHspKdfAXg",
    )
    e = Event(
        id="0x02a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae",
        origin="test",
        document_id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="Event test data",
        timestamp_source="block",
        sender="did:ebsi:zE971oT9esuKdcHspKdfAXg",
        external_hash="0x02a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae",
    )
    e2 = Event(
        id="0x03a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae",
        origin="test",
        document_id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="Event test data 2",
        timestamp_source="block",
        sender="did:ebsi:zE971oT9esuKdcHspKdfAXg",
        external_hash="0x03a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae",
    )
    session.add(d)
    session.add(e)
    session.add(e2)
    session.commit()

    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/events")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_not_found_events(client: TestClient):
    response = client.get("/track-and-trace/documents/fake/events")
    assert response.status_code == 404


def test_read_document_event(client, session):
    d = Document(
        id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="This is a test document",
        timestamp_source="block",
        creator="did:ebsi:zE971oT9esuKdcHspKdfAXg",
    )
    e = Event(
        id="0x02a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae",
        origin="test",
        document_id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="Event test data",
        timestamp_source="block",
        sender="did:ebsi:zE971oT9esuKdcHspKdfAXg",
        external_hash="0x02a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae",
    )
    session.add(d)
    session.add(e)
    session.commit()

    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/events/0x02a09bf88268028d1ca221305bd460db856c696a47cd58949aca0803eedc62ae")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_event_not_found(client: TestClient):
    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/events/fake")
    assert response.status_code == 404


def test_read_document_accesses(client, session):
    d = Document(
        id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        metadata_text="This is a test document",
        timestamp_source="block",
        creator="did:ebsi:zE971oT9esuKdcHspKdfAXg",
    )
    a = Access(
        permission="write",
        subject="did:ebsi:zE971oT9esuKdcHspKdfAXg",
        document_id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        granted_by="did:ebsi:zE971oT9esuKdcHspKdfAXg"
    )
    a2 = Access(
        permission="delegate",
        subject="did:ebsi:zE971oT9esuKdcHspKdfAXg",
        document_id="0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67",
        granted_by="did:ebsi:zE971oT9esuKdcHspKdfAXg"
    )
    session.add(d)
    session.add(a)
    session.add(a2)
    session.commit()

    response = client.get(
        "/track-and-trace/documents/0xcd299cdabd6299907c31f7cdf112830bda9e2d9f5d33c9fc75dd62caa6b9bd67/accesses")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_document_not_found_accesses(client: TestClient):
    response = client.get("/track-and-trace/documents/fake/accesses")
    assert response.status_code == 404
    assert len(response.json()) > 0
