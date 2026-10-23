from pathlib import Path

import pymupdf
import pytest

PDF_PATH = Path("data/manuals/fronius_symo_10-20kw.pdf")
PNG_PATH = Path("data/pages/fronius_symo_10-20kw")


def test_page_count_matches_pdf():
    if not PDF_PATH.exists():
        pytest.skip("PDF not available - run make download first")
    doc = pymupdf.open(PDF_PATH)
    pdf_page_count = doc.page_count
    png_count = len(list(PNG_PATH.glob("*.png")))
    assert pdf_page_count == png_count
