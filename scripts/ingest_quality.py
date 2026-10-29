import json
from pathlib import Path

from ruamel.yaml import YAML

from ingest.quality import (
    flag_low_text_pages,
    flag_missing_metadata,
    flag_sparse_tables,
    reparse_with_ocr,
)

MANIFEST_PATH = Path("corpus/manifest.yaml")
PARSED_DIR = Path("data/parsed")
REPORT_PATH = Path("reports/ingest_quality.md")


def main():
    yaml = YAML()
    manifest = yaml.load(MANIFEST_PATH)
    results = {}
    missing_meta = flag_missing_metadata(manifest["manuals"])

    for manual in manifest["manuals"]:
        json_path = PARSED_DIR / f"{manual['id']}.json"
        if not json_path.exists():
            continue

        elements = json.loads(json_path.read_text())["elements"]
        low_text_pages = flag_low_text_pages(elements)
        sparse_tables = flag_sparse_tables(elements)

        results[manual["id"]] = {
            "low_text_pages": low_text_pages,
            "sparse_tables": sparse_tables,
        }

        if low_text_pages:
            ocr_elements = reparse_with_ocr(manual, low_text_pages)
            elements = [e for e in elements if e["page"] not in low_text_pages] + ocr_elements
            cached = json.loads(json_path.read_text())
            json_path.write_text(
                json.dumps(
                    {"sha256": cached["sha256"], "elements": elements},
                    indent=2,
                )
            )
            print(f"updated {manual['id']} with OCR for pages {low_text_pages}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("# Ingest quality report\n\n")

        f.write("## Missing metadata\n")
        if missing_meta:
            for doc_id in missing_meta:
                f.write(f"- {doc_id}\n")
        else:
            f.write("- none\n")
        f.write("\n")

        for doc_id, issues in results.items():
            f.write(f"## {doc_id}\n")
            f.write("### Low-text pages\n")
            if issues["low_text_pages"]:
                for page in issues["low_text_pages"]:
                    f.write(f"- page {page}\n")
            else:
                f.write("- none\n")

            f.write("### Sparse tables\n")
            if issues["sparse_tables"]:
                for t in issues["sparse_tables"]:
                    f.write(f"- page {t['page']}: {t['text']}\n")
            else:
                f.write("- none\n")
            f.write("\n")

    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
