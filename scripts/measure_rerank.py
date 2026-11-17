import time
from statistics import mean

from ingest.index import get_client
from retrieval.rerank import rerank
from retrieval.search import search

QUERIES = [
    "event 34 on SB 2500HF",
    "event 65 SB 3000HF",
    "Symo 10.0 fault 34",
    "event 35 insulation fault",
    "SB 5000TL error 36",
]


def main():
    client = get_client()
    latencies = []

    for q in QUERIES:
        results = search(client, q, model=None, manufacturer=None, k=30)
        start = time.perf_counter()
        rerank(q, results)
        latencies.append(time.perf_counter() - start)

    print(f"mean rerank latency: {mean(latencies):.3f}s")
    print(f"min: {min(latencies):.3f}s max: {max(latencies):.3f}s")


if __name__ == "__main__":
    main()
