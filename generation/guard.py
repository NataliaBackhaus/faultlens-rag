def check_citations(answer: dict, passages: list[dict]) -> dict:
    filtered_citations = []
    valid = {(p["doc_id"], p["page"]) for p in passages}

    for citation in answer["citations"]:
        parts = citation.split()
        if len(parts) < 3:
            continue
        doc_id = parts[1]
        try:
            page = int(parts[2].replace("p.", ""))
        except ValueError:
            continue
        if (doc_id, page) in valid:
            filtered_citations.append(citation)
    answer["citations"] = filtered_citations

    return answer


def should_abstain(rerank_scores: list[float], threshold: float = 0.0) -> bool:
    if not rerank_scores or max(rerank_scores) < threshold:
        return True
    return False


def wrong_model_abstain(passages: list[dict], queried_model: str | None) -> dict | None:
    if queried_model is None:
        return None

    passages_diff = []

    for p in passages:
        if p["doc_id"] != queried_model:
            passages_diff.append(p["doc_id"])

    if len(passages_diff) == len(passages):
        other_model = max(set(passages_diff), key=passages_diff.count)
        reason = f"Information found for {other_model}, not for {queried_model}"
        return {"abstain": True, "reason": reason}

    return None
