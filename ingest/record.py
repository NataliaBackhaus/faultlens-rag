from dataclasses import dataclass


@dataclass
class Record:
    doc_id: str
    # "prose" | "table_row" | "table" | "figure"
    record_type: str
    text: str
    page: int
    bbox: list[float]
    section_path: str
    manufacturer: str
    models: list[str]
    firmware: str | None
    error_codes: list[str]

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)
