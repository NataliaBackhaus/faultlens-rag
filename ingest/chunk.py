import json
from pathlib import Path

from ingest.record import Record

MAX_CHARS = 1500
_FIGURE_DESCRIPTIONS_PATH = Path("data/figure_descriptions.jsonl")
OVERLAP_CHARS = 200
WARNING_PREFIXES = ("WARNING", "CAUTION", "DANGER", "NOTE")


def chunk_text(text: str) -> list[str]:
    if len(text) <= MAX_CHARS:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = []

    for p in paragraphs:
        joined = "\n\n".join(current)
        if joined and len(joined) + len(p) >= MAX_CHARS:
            chunks.append(joined)
            current = [joined[-OVERLAP_CHARS:]]

        current.append(p)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _make_prose_records(
    section_path: str, texts: list[str], page: int, bbox: list[float], doc_meta: dict
) -> list[Record]:

    joined = "\n\n".join(texts)
    chunks = chunk_text(joined)
    records = []

    for chunk in chunks:
        records.append(
            Record(
                doc_id=doc_meta["doc_id"],
                record_type="prose",
                text=chunk,
                page=page,
                bbox=bbox,
                section_path=section_path,
                manufacturer=doc_meta["manufacturer"],
                models=doc_meta["models"],
                firmware=doc_meta["firmware_range"],
                error_codes=[],
            )
        )
    return records


def load_figure_descriptions() -> dict[tuple[str, int, int], str]:
    if not _FIGURE_DESCRIPTIONS_PATH.exists():
        return {}
    descriptions: dict[tuple[str, int, int], str] = {}
    with open(_FIGURE_DESCRIPTIONS_PATH) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                key = (entry["doc_id"], entry["page"], entry["bbox_left"])
                descriptions[key] = entry["description"]
    return descriptions


def chunk_document(
    elements: list[dict],
    doc_meta: dict,
    figure_descriptions: dict[tuple[str, int, int], str] | None = None,
) -> list[Record]:
    records = []
    current_texts = []
    current_section = None
    current_page = 0
    current_bbox = [0.0, 0.0, 0.0, 0.0]

    for elem in elements:
        etype = elem["type"]
        section = elem.get("section_path", "")
        page = elem.get("page", 0)
        bbox = elem.get("bbox", [0.0, 0.0, 0.0, 0.0])
        text = elem.get("text", "").strip()

        if etype == "text":
            if section != current_section and not text.startswith(WARNING_PREFIXES):
                if current_texts:
                    records.extend(
                        _make_prose_records(
                            current_section, current_texts, current_page, current_bbox, doc_meta
                        )
                    )
                current_texts = [text]
                current_section = section
                current_page = page
                current_bbox = bbox

            elif text.startswith(WARNING_PREFIXES):
                current_texts.append(text)

            else:
                current_texts.append(text)
                current_page = page
                current_bbox = bbox

        elif etype == "table":
            if current_texts:
                records.extend(
                    _make_prose_records(
                        current_section, current_texts, current_page, current_bbox, doc_meta
                    )
                )
                current_texts = []
                current_section = None

            records.append(
                Record(
                    doc_id=doc_meta["doc_id"],
                    record_type="table",
                    text=text,
                    page=page,
                    bbox=bbox,
                    section_path=section,
                    manufacturer=doc_meta["manufacturer"],
                    models=doc_meta["models"],
                    firmware=doc_meta["firmware_range"],
                    error_codes=[],
                )
            )

            for line in text.split("\n")[2:]:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if not cells or not cells[0].isdigit():
                    continue
                records.append(
                    Record(
                        doc_id=doc_meta["doc_id"],
                        record_type="table_row",
                        text=" | ".join(cells),
                        page=page,
                        bbox=bbox,
                        section_path=section,
                        manufacturer=doc_meta["manufacturer"],
                        models=doc_meta["models"],
                        firmware=doc_meta["firmware_range"],
                        error_codes=[cells[0]],
                    )
                )

        elif etype == "figure":
            if current_texts:
                records.extend(
                    _make_prose_records(
                        current_section, current_texts, current_page, current_bbox, doc_meta
                    )
                )
                current_texts = []
                current_section = None

            fig_key = (doc_meta["doc_id"], page, int(bbox[0]))
            fig_text = figure_descriptions.get(fig_key, text) if figure_descriptions else text
            records.append(
                Record(
                    doc_id=doc_meta["doc_id"],
                    record_type="figure",
                    text=fig_text,
                    page=page,
                    bbox=bbox,
                    section_path=section,
                    manufacturer=doc_meta["manufacturer"],
                    models=doc_meta["models"],
                    firmware=doc_meta["firmware_range"],
                    error_codes=[],
                )
            )
    if current_texts:
        records.extend(
            _make_prose_records(
                current_section, current_texts, current_page, current_bbox, doc_meta
            )
        )

    return records
