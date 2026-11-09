from ingest.record import Record

MAX_CHARS = 1500
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


def chunk_document(elements: list[dict], doc_meta: dict) -> list[Record]:
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

        elif etype == "figure":
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
                    record_type="figure",
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
    if current_texts:
        records.extend(
            _make_prose_records(
                current_section, current_texts, current_page, current_bbox, doc_meta
            )
        )

    return records
