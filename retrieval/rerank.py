from sentence_transformers import CrossEncoder

RERANKER_MODEL = "BAAI/bge-reranker-base"

_reranker = CrossEncoder(RERANKER_MODEL)


def rerank(query: str, results: list[dict], top_n: int = 5) -> list[dict]:
    if not results:
        return results
    pairs = [[query, r["text"]] for r in results]
    scores = _reranker.predict(pairs)
    ranked = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
    return [r for _, r in ranked[:top_n]]
