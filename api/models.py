"""Pydantic request and response models for the FaultLens API."""

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    model: str | None = None
    firmware: str | None = None


class Citation(BaseModel):
    ref: str
    doc_id: str
    page: int
    page_image_url: str


class AskResponse(BaseModel):
    diagnosis: str
    causes: list[str]
    steps: list[str]
    safety: list[str]
    citations: list[Citation]
    abstained: bool
