import json
import time
from dataclasses import asdict
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.types.doc import ListItem, PictureItem, SectionHeaderItem, TableItem, TextItem
from ruamel.yaml import YAML

from ingest.element import Element

MANIFEST_PATH = Path("corpus/manifest.yaml")
MANUALS_DIR = Path("data/manuals")
PARSED_DIR = Path("data/parsed")


def parse_manual(manual: dict) -> list[Element]:

    pdf_path = MANUALS_DIR / f"{manual['id']}.pdf"

    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    doc = result.document

    elements = []
    heading_stack = []

    for item, level in doc.iterate_items():
        text = getattr(item, "text", "").strip()

        if isinstance(item, SectionHeaderItem):
            heading_stack = heading_stack[: level - 1] + [item.text]
            elem_type = "heading"
        elif isinstance(item, TableItem):
            elem_type = "table"
        elif isinstance(item, PictureItem):
            elem_type = "figure"
        elif isinstance(item, (TextItem, ListItem)):
            elem_type = "text"
        else:
            continue

        page, bbox = 1, [0.0, 0.0, 0.0, 0.0]
        if item.prov:
            prov = item.prov[0]
            page = prov.page_no
            bbox = [prov.bbox.l, prov.bbox.t, prov.bbox.r, prov.bbox.b]

        elements.append(
            Element(
                type=elem_type,
                text=text,
                page=page,
                bbox=bbox,
                section_path=" > ".join(heading_stack),
            )
        )

    return elements


def main():
    yaml = YAML()
    manifest = yaml.load(MANIFEST_PATH)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    for manual in manifest["manuals"]:
        out_path = PARSED_DIR / f"{manual['id']}.json"
        current_hash = manual.get("sha256")
        if out_path.exists():
            cached = json.loads(out_path.read_text())
            if cached.get("sha256") == current_hash:
                print(f"skip {manual['id']}")
                continue

        t0 = time.time()
        elements = parse_manual(manual)
        elapsed = time.time() - t0
        print(f"parsed {manual['id']} in {elapsed:.1f}s - {len(elements)} elements")

        out_path.write_text(
            json.dumps(
                {
                    "sha256": current_hash,
                    "elements": [asdict(e) for e in elements],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
