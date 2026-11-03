import json
from pathlib import Path

import pytest

from ingest.figures import crop_figure, is_decorative

PAGE_H_PT = 595.0  # A4 height in points
PAGES_DIR = Path("data/pages")
PARSED_DIR = Path("data/parsed")


def make_figure(left, top, right, bottom, page=10, section="Section") -> dict:
    return {
        "type": "figure",
        "text": "",
        "page": page,
        "bbox": [left, top, right, bottom],
        "section_path": section,
    }


# --- is_decorative ---


def test_normal_figure_not_decorative():
    # large figure in the middle of the page
    elem = make_figure(50, 400, 300, 150)
    assert is_decorative(elem, PAGE_H_PT) is False


def test_too_narrow_is_decorative():
    elem = make_figure(50, 300, 70, 150)  # width = 20 < 30
    assert is_decorative(elem, PAGE_H_PT) is True


def test_too_short_is_decorative():
    elem = make_figure(50, 170, 300, 150)  # height = 20 < 30
    assert is_decorative(elem, PAGE_H_PT) is True


def test_header_zone_is_decorative():
    # b > 0.90 * 595 = 535.5 → logo in top margin
    elem = make_figure(50, 590, 200, 560)
    assert is_decorative(elem, PAGE_H_PT) is True


def test_footer_zone_is_decorative():
    # t < 0.10 * 595 = 59.5 → decoration in bottom margin
    elem = make_figure(50, 40, 200, 10)
    assert is_decorative(elem, PAGE_H_PT) is True


def test_just_outside_header_zone_not_decorative():
    # b = 530 < 535.5 → not in header
    elem = make_figure(50, 580, 200, 530)
    assert is_decorative(elem, PAGE_H_PT) is False


def test_just_outside_footer_zone_not_decorative():
    # t = 65 > 59.5 → not in footer
    elem = make_figure(50, 65, 200, 35)  # height = 30, t = 65
    assert is_decorative(elem, PAGE_H_PT) is False


# --- crop_figure ---

DOC_ID = "sma_sunnyboy_hf_2-3kw"


def load_figures():
    path = PARSED_DIR / f"{DOC_ID}.json"
    if not path.exists():
        pytest.skip(f"{DOC_ID}.json not available — run ingest first")
    if not (PAGES_DIR / DOC_ID).exists():
        pytest.skip(f"page renders for {DOC_ID} not available — run render_pages first")
    data = json.loads(path.read_text())
    return [e for e in data["elements"] if e["type"] == "figure"]


def test_crop_figure_returns_dict():
    figures = load_figures()
    # find first non-decorative figure
    from PIL import Image

    from ingest.figures import SCALE, is_decorative

    for fig in figures:
        img = Image.open(PAGES_DIR / DOC_ID / f"{fig['page']:04d}.png")
        page_h_pt = img.height / SCALE
        if not is_decorative(fig, page_h_pt):
            result = crop_figure(fig, DOC_ID)
            assert isinstance(result, dict)
            assert result["doc_id"] == DOC_ID
            assert isinstance(result["page"], int)
            assert "path" in result and "bbox" in result
            return
    pytest.skip("no non-decorative figures found")


def test_crop_figure_file_exists():
    figures = load_figures()
    from PIL import Image

    from ingest.figures import SCALE, is_decorative

    for fig in figures:
        img = Image.open(PAGES_DIR / DOC_ID / f"{fig['page']:04d}.png")
        page_h_pt = img.height / SCALE
        if not is_decorative(fig, page_h_pt):
            result = crop_figure(fig, DOC_ID)
            assert Path(result["path"]).exists()
            return
    pytest.skip("no non-decorative figures found")


def test_crop_figure_decorative_returns_none():
    # small icon: 10x10 points
    elem = make_figure(50, 310, 60, 300, page=1)
    result = crop_figure(elem, DOC_ID)
    assert result is None
