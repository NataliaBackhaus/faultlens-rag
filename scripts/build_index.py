import json
from pathlib import Path

from ruamel.yaml import YAML

from ingest.chunk import chunk_document
from ingest.index import (
    COLLECTION_NAME,
    create_collection,
    create_payload_indexes,
    get_client,
    upsert_records,
)
from ingest.metadata import extract_metadata

MANIFEST_PATH = Path("corpus/manifest.yaml")
PARSED_DIR = Path("data/parsed")


def main():
    yaml = YAML()
    manifest = yaml.load(MANIFEST_PATH)

    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        create_collection(client)
        create_payload_indexes(client)

    for manual in manifest["manuals"]:
        doc_id = manual["id"]
        parsed_path = PARSED_DIR / f"{doc_id}.json"
        if not parsed_path.exists():
            print(f"skip {doc_id} - parsed JSON not found")
            continue

        elements = json.loads(parsed_path.read_text())["elements"]
        metadata = extract_metadata(elements)
        metadata["doc_id"] = doc_id
        records = chunk_document(elements, metadata)
        upsert_records(client, records)
        print(f"{doc_id}: {len(records)} records indexed")

    snapshot = client.create_snapshot(collection_name=COLLECTION_NAME)
    print(f"snapshot saved: {snapshot.name}")


if __name__ == "__main__":
    main()
