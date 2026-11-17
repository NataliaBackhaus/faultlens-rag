def recall_at_k(results: list[dict], gold_doc: str, gold_page: int, k: int) -> float:
    for result in results[:k]:
        if result["page"] == gold_page and result["doc_id"] == gold_doc:
            return 1.0
    return 0.0


def mrr(results: list[dict], gold_doc: str, gold_page: int) -> float:
    for i, result in enumerate(results):
        if result["page"] == gold_page and result["doc_id"] == gold_doc:
            return 1.0 / (i + 1)
    return 0.0


def wrong_model_rate(results: list[dict], gold_doc: str | None) -> float:
    if not results:
        return 0.0
    if gold_doc is None:
        return 1.0
    wrong = sum(1 for r in results if r.get("doc_id") != gold_doc)
    return wrong / len(results)
