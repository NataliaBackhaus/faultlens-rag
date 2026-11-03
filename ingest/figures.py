from pathlib import Path

from PIL import Image

PAGES_DIR = Path("data/pages")
FIGURES_DIR = Path("data/figures")

DPI = 150
SCALE = DPI / 72
MARGIN = 10  # pixels

MIN_WIDTH_PT = 30
MIN_HEIGHT_PT = 30
HEADER_RATIO = 0.90
FOOTER_RATIO = 0.10


def is_decorative(elem: dict, page_h_pt: float) -> bool:
    """Return True if the figure is likely a logo or decoration to be dropped."""
    left, top, right, bottom = elem["bbox"]

    width = right - left
    height = top - bottom

    if width < MIN_WIDTH_PT or height < MIN_HEIGHT_PT:
        return True

    if bottom > HEADER_RATIO * page_h_pt:
        return True

    if top < FOOTER_RATIO * page_h_pt:
        return True

    return False


def crop_figure(elem: dict, doc_id: str) -> dict | None:
    """Crop a figure element from its page render and save to data/figures/."""
    page = elem["page"]
    left, top, right, bottom = elem["bbox"]

    img = Image.open(PAGES_DIR / doc_id / f"{page:04d}.png")
    page_h = img.height

    left_px = max(0, int(left * SCALE) - MARGIN)
    top_px = max(0, int(page_h - top * SCALE) - MARGIN)
    right_px = min(img.width, int(right * SCALE) + MARGIN)
    bottom_px = min(page_h, int(page_h - bottom * SCALE) + MARGIN)

    page_h_pt = img.height / SCALE

    if is_decorative(elem, page_h_pt):
        return None

    crop = img.crop((left_px, top_px, right_px, bottom_px))

    out_dir = FIGURES_DIR / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{page:04d}_{int(left):04d}.png"
    crop.save(out_path)

    return {
        "doc_id": doc_id,
        "page": page,
        "path": str(out_path),
        "bbox": elem["bbox"],
        "section_path": elem.get("section_path", ""),
        "caption": elem.get("text", ""),
    }
