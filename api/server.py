"""Minimal FastAPI app — page image endpoint."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response

from api.page_image import PAGES_DIR, annotate_page

app = FastAPI(title="FaultLens RAG", version="0.1.0")


@app.get("/pages/{doc_id}/{page}", response_class=Response)
def get_page(
    doc_id: str,
    page: int,
    bbox: str | None = Query(
        default=None,
        description="Bounding box as 'x0,y_top,x1,y_bottom' in PDF points. "
        "When present, the region is highlighted in red.",
    ),
):
    """Return the rendered page PNG, optionally annotated with a bbox rectangle."""
    if bbox is not None:
        try:
            coords = [float(v) for v in bbox.split(",")]
        except ValueError:
            raise HTTPException(status_code=422, detail="bbox must be four comma-separated floats")
        if len(coords) != 4:
            raise HTTPException(status_code=422, detail="bbox must contain exactly four values")
        try:
            image_bytes = annotate_page(doc_id, page, coords)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return Response(content=image_bytes, media_type="image/jpeg")

    path: Path = PAGES_DIR / doc_id / f"{page:04d}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Page image not found: {path}")
    return FileResponse(path, media_type="image/png")
