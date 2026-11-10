import pytest
from qdrant_client import QdrantClient

from ingest.index import (
    COLLECTION_NAME,
    create_collection,
    create_payload_indexes,
    get_client,
    upsert_records,
)
from ingest.record import Record


def qdrant_available() -> bool:
    try:
        get_client().get_collections()
        return True
    except Exception:
        return False


requires_qdrant = pytest.mark.skipif(not qdrant_available(), reason="Qdrant not running")

SAMPLE_RECORD = Record(
    doc_id="test_doc",
    record_type="prose",
    text="The inverter switches off due to overtemperature.",
    page=1,
    bbox=[0.0, 100.0, 200.0, 50.0],
    section_path="10 Troubleshooting",
    manufacturer="SMA",
    models=["SB 2500HF"],
    firmware=None,
    error_codes=[],
)


def test_get_client_returns_qdrant_client():
    client = get_client()
    assert isinstance(client, QdrantClient)


def test_upsert_records_empty_list_does_not_raise():
    client = get_client()
    upsert_records(client, [], batch_size=64)


@requires_qdrant
def test_collection_exists_after_create():
    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        create_collection(client)
    assert client.collection_exists(COLLECTION_NAME)


@requires_qdrant
def test_payload_indexes_do_not_raise():
    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        create_collection(client)
    create_payload_indexes(client)


@requires_qdrant
def test_upsert_records_increases_point_count():
    client = get_client()
    before = client.get_collection(COLLECTION_NAME).points_count
    upsert_records(client, [SAMPLE_RECORD], batch_size=64)
    after = client.get_collection(COLLECTION_NAME).points_count
    assert after > before


@requires_qdrant
def test_collection_has_dense_and_sparse_vectors():
    client = get_client()
    info = client.get_collection(COLLECTION_NAME)
    assert "dense" in info.config.params.vectors
    assert "bm25" in (info.config.params.sparse_vectors or {})
