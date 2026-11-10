import uuid

from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient, models

from ingest.record import Record

COLLECTION_NAME = "faultlens"
QDRANT_URL = "http://localhost:6333"
DENSE_DIM = 768

DENSE_MODEL = "BAAI/bge-base-en-v1.5"
SPARSE_MODEL = "Qdrant/bm25"


def get_client():
    client = QdrantClient(url=QDRANT_URL)
    return client


def create_collection(client):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": models.VectorParams(size=DENSE_DIM, distance=models.Distance.COSINE)
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
        },
    )


def create_payload_indexes(client):
    for field, schema_type in [
        ("manufacturer", models.PayloadSchemaType.KEYWORD),
        ("models", models.PayloadSchemaType.KEYWORD),
        ("firmware", models.PayloadSchemaType.KEYWORD),
        ("record_type", models.PayloadSchemaType.KEYWORD),
        ("error_codes", models.PayloadSchemaType.KEYWORD),
    ]:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field,
            field_schema=schema_type,
        )


def upsert_records(client, records: list[Record], batch_size: int = 64) -> None:
    dense_model = TextEmbedding(model_name=DENSE_MODEL)
    sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL)

    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        texts = [r.text for r in batch]

        dense_vecs = list(dense_model.embed(texts, batch_size=batch_size))
        sparse_vecs = list(sparse_model.embed(texts, batch_size=batch_size))

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    payload=record.to_dict(),
                    vector={
                        "dense": dv.tolist(),
                        "bm25": models.SparseVector(
                            indices=sv.indices.tolist(),
                            values=sv.values.tolist(),
                        ),
                    },
                )
                for record, dv, sv in zip(batch, dense_vecs, sparse_vecs)
            ],
        )
