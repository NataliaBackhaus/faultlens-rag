from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchValue,
    Prefetch,
    SparseVector,
)

from ingest.index import COLLECTION_NAME, DENSE_MODEL, SPARSE_MODEL
from retrieval.query import parse_query


def build_filter(model: str | None, manufacturer: str | None) -> Filter | None:
    conditions = []

    if model:
        conditions.append(FieldCondition(key="models", match=MatchValue(value=model)))

    if manufacturer:
        conditions.append(FieldCondition(key="manufacturer", match=MatchValue(value=manufacturer)))

    if not conditions:
        return None

    return Filter(must=conditions)


def exact_code_lookup(client, error_code: str, model: str | None) -> list[dict]:
    code_filter = Filter(
        must=[
            FieldCondition(key="record_type", match=MatchValue(value="table_row")),
            FieldCondition(key="error_codes", match=MatchValue(value=error_code)),
        ]
    )

    if model:
        code_filter.must.append(FieldCondition(key="models", match=MatchValue(value=model)))

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=code_filter,
        limit=5,
        with_payload=True,
    )

    return [p.payload for p in points]


def search(
    client, query: str, model: str | None, manufacturer: str | None, k: int = 10
) -> list[dict]:
    dense_model = TextEmbedding(model_name=DENSE_MODEL)
    sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL)

    dense_vec = list(dense_model.embed([query]))[0].tolist()
    sparse_obj = list(sparse_model.embed([query]))[0]
    sparse_vec = SparseVector(
        indices=sparse_obj.indices.tolist(), values=sparse_obj.values.tolist()
    )

    filters = build_filter(model, manufacturer)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(query=dense_vec, using="dense", filter=filters, limit=k * 2),
            Prefetch(query=sparse_vec, using="bm25", filter=filters, limit=k * 2),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=k,
        with_payload=True,
    )

    return [p.payload for p in results.points]


def _manufacturer_from_model(model: str) -> str | None:
    if model.startswith("sma_"):
        return "SMA"

    if model.startswith("fronius_"):
        return "Fronius"

    return None


def retrieve(client, query_text: str) -> list[dict]:
    parsed = parse_query(query_text)

    if parsed["error_code"]:
        results = exact_code_lookup(client, parsed["error_code"], parsed["model"])
        if results:
            return results

    results = search(client, query_text, parsed["model"], manufacturer=None)

    if not results and parsed["model"]:
        manufacturer = _manufacturer_from_model(parsed["model"])
        results = search(client, query_text, model=None, manufacturer=manufacturer)
        for r in results:
            r["_manufacturer_fallback"] = True

    return results
