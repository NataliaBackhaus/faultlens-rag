import json
import re

MANUFACTURERS = ["SMA", "Fronius"]
FAMILIES = ["Sunny Boy", "Symo", "SYMO", "SB", "Tripower"]
MODEL_TABLE_HEADERS = {"model", "type", "device", "applies to", "valid for", "inverter"}

MODEL_PATTERN = re.compile(r"\b[A-Z]{1,5}[-\s]?\d+[\d.\-]*[A-Z0-9\-]*\b")
REVISION_PATTERN = re.compile(r"[Rr]ev(?:ision)?\.?\s*([\d.]+)")


def extract_with_regex(elements: list[dict]) -> dict:
    """Extract device metadata from title page and headings using regex."""
    result = {
        "manufacturer": None,
        "product_family": None,
        "models": [],
        "firmware_range": None,
        "revision": None,
        "source": "regex",
    }
    early = [e for e in elements if e["page"] <= 5]
    text = " ".join(e["text"] for e in early)

    # manufacturer
    for m in MANUFACTURERS:
        if m in text:
            result["manufacturer"] = m
            break

    # product family
    for f in FAMILIES:
        if f in text:
            result["product_family"] = f
            break

    # models
    result["models"] = MODEL_PATTERN.findall(text)

    # revision
    match = REVISION_PATTERN.search(text)
    if match:
        result["revision"] = match.group(1)

    return result


def extract_with_llm(elements: list[dict], llm) -> dict:
    """Fill metadata gaps using LLM with a strict JSON schema."""
    early = [e for e in elements if e["page"] <= 5]
    text = " ".join(e["text"] for e in early)[:3000]

    prompt = f"""Extract device metadata from this inverter manual text.
    Return ONLY a JSON object with these fields:
    - manufacturer: string (e.g. "SMA" or "Fronius")
    - product_family: string (e.g. "Sunny Boy" or "Symo")
    - models: list of strings (e.g. ["SB 2500HF-30"])
    - firmware_range: string or null
    - revision: string or null

    Text:
    {text}"""

    response = llm.generate(prompt)
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        result = json.loads(match.group())
        result["source"] = "llm"
        return result
    return {}


def _normalize(s: str) -> str:
    return re.sub(r"[\s\-.]", "", s).lower()


def narrow_models_from_tables(elements: list[dict], models: list[str]) -> list[str]:
    """Scan tables for model-listing columns; return only models that appear there."""
    if not models:
        return models

    found = set()
    for elem in elements:
        if elem["type"] != "table":
            continue

        lines = elem["text"].split("\n")
        cells = [c.strip().lower() for c in lines[0].strip().strip("|").split("|")]
        model_col = None

        for i, cell in enumerate(cells):
            if cell in MODEL_TABLE_HEADERS:
                model_col = i
                break

        if model_col is None:
            continue

        for line in lines[2:]:
            if not line.strip():
                continue
            row_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if model_col < len(row_cells):
                found.add(row_cells[model_col])

    if not found:
        return models

    norm_found = {_normalize(v) for v in found}
    narrowed = [m for m in models if _normalize(m) in norm_found]
    return narrowed if narrowed else models


def extract_metadata(elements: list[dict], llm=None) -> dict:
    """Extract metadata using regex first, LLM for gaps."""
    result = extract_with_regex(elements)
    if llm and not (result["manufacturer"] and result["models"]):
        result = extract_with_llm(elements, llm)
    result["models"] = narrow_models_from_tables(elements, result["models"])
    return result
