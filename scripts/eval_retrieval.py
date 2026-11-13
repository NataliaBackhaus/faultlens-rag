import csv
import json
import os
import subprocess
from datetime import UTC, datetime
from statistics import mean

from eval.metrics import mrr, recall_at_k, wrong_model_rate
from ingest.index import get_client
from retrieval.search import retrieve


def main():
    with open("eval/questions.jsonl") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    client = get_client()
    all_recall_5 = []
    all_recall_10 = []
    all_mrr = []
    all_wmr = []

    for q in questions:
        results = retrieve(client, q["question"])
        all_recall_5.append(recall_at_k(results, q["gold_doc"], q["gold_page"], k=5))
        all_recall_10.append(recall_at_k(results, q["gold_doc"], q["gold_page"], k=10))
        all_mrr.append(mrr(results, q["gold_doc"], q["gold_page"]))
        all_wmr.append(wrong_model_rate(results, q["model"]))

    mean_recall_5 = mean(all_recall_5)
    mean_recall_10 = mean(all_recall_10)
    mean_mrr = mean(all_mrr)
    mean_wmr = mean(all_wmr)

    print(f"recall@5: {mean_recall_5:.3f}")
    print(f"recall@10: {mean_recall_10:.3f}")
    print(f"mrr: {mean_mrr:.3f}")
    print(f"wrong_model_rate: {mean_wmr:.3f}")

    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    row = {
        "date": datetime.now(tz=UTC).strftime("%Y-%m-%d"),
        "commit": commit,
        "recall@5": round(mean_recall_5, 3),
        "recall@10": round(mean_recall_10, 3),
        "mrr": round(mean_mrr, 3),
        "wrong_model_rate": round(mean_wmr, 3),
    }

    csv_path = "eval/history.csv"
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    main()
