"""Annotate a rendered page PNG with the bounding box of a cited record."""

import io
from pathlib import Path

from PIL import Image, ImageDraw

PAGES_DIR = Path("data/pages")
RENDER_DPI = 150
PDF_DPI = 72
SCALE = RENDER_DPI / PDF_DPI
BBOX_COLOR = "red"
BBOX_WIDTH = 3


def annotate_page(doc_id: str, page: int, bbox: list[float]) -> bytes:
    """Return JPEG bytes of the page PNG with bbox drawn.

    bbox: [x0, y_top, x1, y_bottom] in PDF points (72 DPI, y-axis bottom-up).
    Raises FileNotFoundError when the page PNG does not exist.
    """
    path = PAGES_DIR / doc_id / f"{page:04d}.png"
    if not path.exists():
        raise FileNotFoundError(f"Page image not found: {path}")

    img = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(img)

    x0, y_top_pdf, x1, y_bottom_pdf = bbox
    h = img.height

    # PDF y-axis is bottom-up; PIL y-axis is top-down - flip.
    x0_px = x0 * SCALE
    y0_px = h - y_top_pdf * SCALE
    x1_px = x1 * SCALE
    y1_px = h - y_bottom_pdf * SCALE

    draw.rectangle([x0_px, y0_px, x1_px, y1_px], outline=BBOX_COLOR, width=BBOX_WIDTH)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf.getvalue()
