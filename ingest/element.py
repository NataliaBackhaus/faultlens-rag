from dataclasses import dataclass


@dataclass
class Element:
    type: str  # "text", "heading", "table", "figure"
    text: str  # textual content of the element
    page: int  # 1-indexed page number
    bbox: list[float]  # [x0, y0, x1, y1] in page points
    section_path: str  # heading hierarchy, e.g. "3. Installation > 3.2 AC Connection"
