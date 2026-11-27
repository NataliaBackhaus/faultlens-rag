"""FaultLens RAG - FastAPI service."""

import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, Response

from api.models import AskRequest, AskResponse, Citation, FeedbackRequest
from api.page_image import PAGES_DIR, annotate_page
from feedback.store import save_feedback
from generation.answer import generate_answer
from generation.guard import check_citations, should_abstain, wrong_model_abstain
from generation.llm_client import OllamaClient
from ingest.index import get_client
from retrieval.search import retrieve

# MODEL_TO_DOC maps the human-readable model name from the request to the
# doc_id used inside Qdrant - needed by wrong_model_abstain.
MODEL_TO_DOC: dict[str, str] = {
    "SB 2000HF": "sma_sunnyboy_hf_2-3kw",
    "SB 2500HF": "sma_sunnyboy_hf_2-3kw",
    "SB 3000HF": "sma_sunnyboy_hf_2-3kw",
    "SB 3000TL": "sma_sunnyboy_tl_3-5kw",
    "SB 4000TL": "sma_sunnyboy_tl_3-5kw",
    "SB 5000TL": "sma_sunnyboy_tl_3-5kw",
    "Fronius Symo 10.0-3-M": "fronius_symo_10-20kw",
    "Fronius Symo 15.0-3-M": "fronius_symo_10-20kw",
    "Fronius Symo 17.5-3-M": "fronius_symo_10-20kw",
    "Fronius Symo 20.0-3-M": "fronius_symo_10-20kw",
    "Fronius Symo 24.0-3-M": "fronius_symo_10-20kw",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.qdrant = get_client()
    app.state.llm = OllamaClient()
    yield


app = FastAPI(title="FaultLens RAG", version="0.1.0", lifespan=lifespan)


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, request: Request):
    qdrant = request.app.state.qdrant
    llm = request.app.state.llm
    trace_id = str(uuid.uuid4())

    passages = retrieve(qdrant, body.question)
    rerank_scores = [p.get("_score", 0.0) for p in passages]

    if should_abstain(rerank_scores):
        return AskResponse(
            trace_id=trace_id,
            abstained=True,
            diagnosis="",
            causes=[],
            steps=[],
            safety=[],
            citations=[],
        )

    doc_id = MODEL_TO_DOC.get(body.model)
    if wrong_model_abstain(passages, doc_id):
        return AskResponse(
            trace_id=trace_id,
            abstained=True,
            diagnosis="",
            causes=[],
            steps=[],
            safety=[],
            citations=[],
        )
    answer = generate_answer(llm, body.question, passages)
    answer = check_citations(answer, passages)

    citations = []

    for c in answer["citations"]:
        parts = c.split()
        ref = parts[0]
        cit_doc_id = parts[1]
        page = int(parts[2].replace("p.", ""))
        citations.append(
            Citation(
                ref=ref,
                doc_id=cit_doc_id,
                page=page,
                page_image_url=f"/pages/{cit_doc_id}/{page}",
            )
        )

    return AskResponse(
        trace_id=trace_id,
        abstained=False,
        diagnosis=answer["diagnosis"],
        causes=answer["causes"],
        steps=answer["steps"],
        safety=answer["safety"],
        citations=citations,
    )


@app.post("/feedback", status_code=204)
def feedback(body: FeedbackRequest):
    if body.vote not in ("up", "down"):
        raise HTTPException(status_code=422, detail="vote must be 'up' or 'down'")
    save_feedback(body.trace_id, body.question, body.vote)
