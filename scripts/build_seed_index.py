"""Build eval/seed_index from the live Qdrant collection.

Run once locally (requires Qdrant Docker on localhost:6333) to generate
the small index that ci_eval.py uses in CI.
"""

import json
import shutil
from pathlib import Path

from qdrant_client import QdrantClient, models

from ingest.index import COLLECTION_NAME, DENSE_DIM, QDRANT_URL

SEED_PATH = Path("eval/seed_index")
SEED_COLLECTION = "faultlens"


def _gold_pages(questions: list[dict]) -> set[tuple[str, int]]:
    pages: set[tuple[str, int]] = set()
    for q in questions:
        if q["gold_doc"] and q["gold_page"] is not None:
            doc, page = q["gold_doc"], int(q["gold_page"])
            for offset in (-1, 0, 1):
                pages.add((doc, page + offset))
    return pages


def main() -> None:
    with open("eval/questions.jsonl") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    target_pages = _gold_pages(questions)
    print(f"Fetching {len(target_pages)} (doc, page) pairs from live index…")

    source = QdrantClient(url=QDRANT_URL)

    all_points: list[models.PointStruct] = []
    seen_ids: set[str] = set()

    for doc_id, page in sorted(target_pages):
        pts, _ = source.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id)),
                    models.FieldCondition(key="page", match=models.MatchValue(value=page)),
                ]
            ),
            limit=20,
            with_payload=True,
            with_vectors=True,
        )
        for pt in pts:
            pt_id = str(pt.id)
            if pt_id not in seen_ids:
                seen_ids.add(pt_id)
                all_points.append(pt)

    print(f"Collected {len(all_points)} unique points.")

    if SEED_PATH.exists():
        shutil.rmtree(SEED_PATH)

    dest = QdrantClient(path=str(SEED_PATH))
    dest.create_collection(
        collection_name=SEED_COLLECTION,
        vectors_config={
            "dense": models.VectorParams(size=DENSE_DIM, distance=models.Distance.COSINE)
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
        },
    )

    for field, schema_type in [
        ("doc_id", models.PayloadSchemaType.KEYWORD),
        ("manufacturer", models.PayloadSchemaType.KEYWORD),
        ("models", models.PayloadSchemaType.KEYWORD),
        ("record_type", models.PayloadSchemaType.KEYWORD),
        ("error_codes", models.PayloadSchemaType.KEYWORD),
    ]:
        dest.create_payload_index(
            collection_name=SEED_COLLECTION,
            field_name=field,
            field_schema=schema_type,
        )

    dest.upsert(collection_name=SEED_COLLECTION, points=all_points)
    print(f"Seed index written to {SEED_PATH}  ({len(all_points)} points)")


if __name__ == "__main__":
    main()
