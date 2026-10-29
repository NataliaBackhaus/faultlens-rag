from dataclasses import asdict
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ListItem, PictureItem, SectionHeaderItem, TableItem, TextItem

from ingest.element import Element

MANUALS_DIR = Path("data/manuals")


def flag_low_text_pages(elements: list[dict], threshold: int = 50) -> list[int]:
    """Returns page numbers where total text length is below threshold."""
    page_text_len = {}
    for e in elements:
        page = e["page"]
        page_text_len[page] = page_text_len.get(page, 0) + len(e["text"])

    return [page for page, total in page_text_len.items() if total < threshold]


def flag_sparse_tables(elements: list[dict], empty_ratio: float = 0.3) -> list[dict]:
    """Returns tables where empty cell ratio exceeds empty_ratio."""
    flagged = []
    for e in elements:
        if e["type"] != "table":
            continue

        cells = [
            cell.strip()
            for row in e["text"].split("\n")
            for cell in row.strip().strip("|").split("|")
        ]

        all_cells = [c for c in cells if not c.startswith("---")]
        if not all_cells:
            continue

        empty_cells = [c for c in all_cells if c == ""]
        if len(empty_cells) / len(all_cells) > empty_ratio:
            flagged.append({"page": e["page"], "text": e["text"][:60]})

    return flagged


def flag_missing_metadata(manuals: list[dict]) -> list[str]:
    """Returns doc ids where sha256 is missing."""
    return [m["id"] for m in manuals if not m.get("sha256")]


def reparse_with_ocr(manual: dict, pages: list[int]) -> list[dict]:
    """Reparse a manual with OCR and return elements only for flagged pages."""
    pdf_path = MANUALS_DIR / f"{manual['id']}.pdf"

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

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

        if page not in pages:
            continue

        elements.append(
            asdict(
                Element(
                    type=elem_type,
                    text=text,
                    page=page,
                    bbox=bbox,
                    section_path=" > ".join(heading_stack),
                )
            )
        )

    return elements
