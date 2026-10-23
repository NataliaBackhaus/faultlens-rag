from pathlib import Path

import pymupdf
from ruamel.yaml import YAML

MANIFEST_PATH = Path("corpus/manifest.yaml")
MANUALS_DIR = Path("data/manuals")
PAGES_DIR = Path("data/pages")


def render_pages(manual: dict):
    """
    Render PDF's pages.
    DPI 150 balances readability for humans and input quality for the vision model
    """

    DPI = 150
    out_dir = PAGES_DIR / manual["id"]
    out_dir.mkdir(parents=True, exist_ok=True)

    path_pdf = MANUALS_DIR / f"{manual['id']}.pdf"
    doc = pymupdf.open(path_pdf)

    for page in doc:
        path_page = out_dir / f"{page.number + 1:04d}.png"
        pix = page.get_pixmap(matrix=pymupdf.Matrix(DPI / 72, DPI / 72))
        pix.save(path_page)


def main():
    yaml = YAML()
    manifest = yaml.load(MANIFEST_PATH)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    for manual in manifest["manuals"]:
        hash_file = PAGES_DIR / manual["id"] / ".hash"
        current_hash = manual.get("sha256")
        if hash_file.exists() and hash_file.read_text() == current_hash:
            print(f"skip {manual['id']}")
            continue

        render_pages(manual)
        hash_file.write_text(current_hash)


if __name__ == "__main__":
    main()
