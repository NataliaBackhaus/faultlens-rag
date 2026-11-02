ERROR_CODE_HEADERS = {
    "code",
    "event",
    "state",
    "message",
    "cause",
    "remedy",
    "measure",
    "fault",
    "result",
    "event no.",
    "event no",
}
COLUMN_ALIASES = {
    "code": {
        "code",
        "event",
        "event number",
        "event no.",
        "event no",
        "state",
        "state number",
        "fault code",
        "no",
    },
    "message": {
        "message",
        "description",
        "event text",
        "text",
        "result",
        "display message and cause",
    },
    "cause": {"cause", "possible cause", "reason"},
    "remedy": {
        "remedy",
        "measure",
        "action",
        "solution",
        "corrective action",
        "corrective measures",
    },
}


def is_error_code_table(table_text: str) -> bool:
    """Returns True if the table's header row contains error-code keywords."""
    header_line = table_text.split("\n")[0]
    cells = [c.strip().lower() for c in header_line.strip().strip("|").split("|")]
    for cell in cells:
        if cell in ERROR_CODE_HEADERS:
            return True
    return False


def map_columns(header_line: str) -> dict[str, int]:
    """Returns {field_name: column_index} for known fields."""
    cells = [c.strip().lower() for c in header_line.strip().strip("|").split("|")]
    mapping = {}
    for i, cell in enumerate(cells):
        for field, aliases in COLUMN_ALIASES.items():
            if cell in aliases:
                mapping[field] = i
    return mapping


def extract_rows(table: dict, doc_id: str) -> list[dict]:
    """Extract error-code rows from a parsed table element."""
    lines = table["text"].split("\n")
    mapping = map_columns(lines[0])
    rows = [{"doc_id": doc_id, "page": table["page"], "type": "table", "raw_table": table["text"]}]
    for line in lines[2:]:
        if not line.strip():
            continue
        cells = [c for c in line.strip().strip("|").split("|")]

        def get(field):
            idx = mapping.get(field)
            return cells[idx].strip() if idx is not None and idx < len(cells) else ""

        rows.append(
            {
                "doc_id": doc_id,
                "page": table["page"],
                "code": get("code"),
                "message": get("message"),
                "cause": get("cause"),
                "remedy": get("remedy"),
                "raw_row": line.strip(),
            }
        )
    return rows


def join_tables(elements: list[dict]) -> list[dict]:
    """Merge error-code tables that continue across consecutive pages."""
    error_tables = [e for e in elements if e["type"] == "table" and is_error_code_table(e["text"])]
    if not error_tables:
        return []

    merged = [error_tables[0].copy()]
    for table in error_tables[1:]:
        prev = merged[-1]
        same_header = table["text"].split("\n")[0] == prev["text"].split("\n")[0]
        consecutive = table["page"] == prev["page"] + 1
        if same_header and consecutive:
            extra_rows = "\n".join(table["text"].split("\n")[2:])
            merged[-1]["text"] = prev["text"] + "\n" + extra_rows
        else:
            merged.append(table.copy())
    return merged
