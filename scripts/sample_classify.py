import csv
import json
import random
from pathlib import Path

from ingest.classify import classify
from ingest.element import Element

PARSED_DIR = Path("data/parsed")
OUT_PATH = Path("data/sample_classify.csv")
SAMPLE_SIZE = 50
SEED = 42


def main():
    all_rows = []
    for json_path in sorted(PARSED_DIR.glob("*.json")):
        doc_id = json_path.stem
        elements = json.loads(json_path.read_text())["elements"]
        for e in elements:
            element = Element(**e)
            tag = classify(element)
            all_rows.append(
                {
                    "doc_id": doc_id,
                    "page": element.page,
                    "type": element.type,
                    "tag": tag,
                    "text": element.text[:80].replace("\n", " "),
                }
            )

    random.seed(SEED)
    sample = random.sample(all_rows, min(SAMPLE_SIZE, len(all_rows)))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "page", "type", "tag", "text"])
        writer.writeheader()
        writer.writerows(sample)

    print(f"wrote {len(sample)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
