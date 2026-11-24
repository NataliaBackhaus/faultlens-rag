import io
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from api.page_image import SCALE, annotate_page


def _make_png(tmp_path: Path, width: int = 875, height: int = 1240) -> Path:
    """Create a plain white PNG at the given path."""
    p = tmp_path / "sma_sunnyboy_hf_2-3kw" / "0026.png"
    p.parent.mkdir(parents=True)
    Image.new("RGB", (width, height), color="white").save(p)
    return p


# ---------------------------------------------------------------------------
# annotate_page
# ---------------------------------------------------------------------------


def test_returns_jpeg_bytes(tmp_path):
    _make_png(tmp_path)
    with patch("api.page_image.PAGES_DIR", tmp_path):
        result = annotate_page("sma_sunnyboy_hf_2-3kw", 26, [38.0, 540.0, 380.0, 450.0])
    assert isinstance(result, bytes)
    assert result[:3] == b"\xff\xd8\xff"  # JPEG magic


def test_output_is_valid_image(tmp_path):
    _make_png(tmp_path)
    with patch("api.page_image.PAGES_DIR", tmp_path):
        result = annotate_page("sma_sunnyboy_hf_2-3kw", 26, [38.0, 540.0, 380.0, 450.0])
    img = Image.open(io.BytesIO(result))
    assert img.width == 875
    assert img.height == 1240


def test_rectangle_is_drawn_in_red(tmp_path):
    _make_png(tmp_path)
    with patch("api.page_image.PAGES_DIR", tmp_path):
        result = annotate_page("sma_sunnyboy_hf_2-3kw", 26, [0.0, 100.0, 50.0, 50.0])
    img = Image.open(io.BytesIO(result)).convert("RGB")
    # The top-left corner of the bbox should be red
    x_px = int(0 * SCALE) + 1
    y_px = int(img.height - 100.0 * SCALE) + 1
    r, g, b = img.getpixel((x_px, y_px))
    assert r > 200 and g < 50 and b < 50


def test_raises_for_missing_page(tmp_path):
    with patch("api.page_image.PAGES_DIR", tmp_path):
        with pytest.raises(FileNotFoundError):
            annotate_page("sma_sunnyboy_hf_2-3kw", 26, [0.0, 100.0, 50.0, 50.0])


# ---------------------------------------------------------------------------
# FastAPI endpoint
# ---------------------------------------------------------------------------


def test_get_page_returns_annotated_jpeg(tmp_path):
    from fastapi.testclient import TestClient

    from api.server import app

    _make_png(tmp_path)
    with patch("api.page_image.PAGES_DIR", tmp_path), patch("api.server.PAGES_DIR", tmp_path):
        client = TestClient(app)
        resp = client.get("/pages/sma_sunnyboy_hf_2-3kw/26?bbox=38,540,380,450")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"


def test_get_page_returns_png_without_bbox(tmp_path):
    from fastapi.testclient import TestClient

    from api.server import app

    _make_png(tmp_path)
    with patch("api.server.PAGES_DIR", tmp_path):
        client = TestClient(app)
        resp = client.get("/pages/sma_sunnyboy_hf_2-3kw/26")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"


def test_get_page_404_for_missing(tmp_path):
    from fastapi.testclient import TestClient

    from api.server import app

    with patch("api.page_image.PAGES_DIR", tmp_path), patch("api.server.PAGES_DIR", tmp_path):
        client = TestClient(app)
        resp = client.get("/pages/sma_sunnyboy_hf_2-3kw/99")
    assert resp.status_code == 404


def test_get_page_422_for_bad_bbox(tmp_path):
    from fastapi.testclient import TestClient

    from api.server import app

    _make_png(tmp_path)
    with patch("api.server.PAGES_DIR", tmp_path):
        client = TestClient(app)
        resp = client.get("/pages/sma_sunnyboy_hf_2-3kw/26?bbox=notanumber")
    assert resp.status_code == 422
