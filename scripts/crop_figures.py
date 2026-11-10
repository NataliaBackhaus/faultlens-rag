import json
from pathlib import Path

from ruamel.yaml import YAML

from ingest.figures import crop_figure

MANIFEST_PATH = Path("corpus/manifest.yaml")
PARSED_DIR = Path("data/parsed")


def main():
    yaml = YAML()
    manifest = yaml.load(MANIFEST_PATH)

    for manual in manifest["manuals"]:
        doc_id = manual["id"]
        parsed_path = PARSED_DIR / f"{doc_id}.json"
        if not parsed_path.exists():
            print(f"skip {doc_id} - parsed JSON not found")
            continue

        data = json.loads(parsed_path.read_text())
        figures = [e for e in data["elements"] if e["type"] == "figure"]

        kept, dropped = 0, 0
        for fig in figures:
            result = crop_figure(fig, doc_id)
            if result is None:
                dropped += 1
            else:
                kept += 1

        print(f"{doc_id}: {kept} crops saved, {dropped} decorative dropped")


if __name__ == "__main__":
    main()
