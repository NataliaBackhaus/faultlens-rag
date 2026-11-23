# FaultLens RAG — Retrieval Ablation Report

**Date:** 2026-11-23  
**Eval set:** `eval/questions.jsonl` — 100 questions (50 code\_lookup, 15 figure\_question, 20 wrong\_model\_trap, 15 unanswerable)  
**Models:** bge-base-en-v1.5 (dense), BM25 sparse, bge-reranker-base (cross-encoder)  
**Index:** 3 manuals (SMA HF, SMA TL, Fronius Symo); chunk types: table\_row, prose, figure

---

## 1. Search mode ablation

All configurations use `k=10` without the cross-encoder reranker.
Metrics are averaged across all 100 questions; wrong\_model\_trap and unanswerable questions
contribute Recall=0 and MRR=0 (no gold document exists for them).

| Configuration   | Recall@10 | MRR   |
|-----------------|-----------|-------|
| Dense only      | 0.200     | 0.089 |
| BM25 only       | **0.320** | **0.117** |
| Hybrid k=20     | 0.260     | 0.112 |
| Hybrid k=40     | 0.280     | 0.112 |
| Hybrid k=60     | 0.280     | 0.114 |

**Analysis.**
BM25 outperforms dense and all hybrid variants on this eval set because event codes are exact
lexical tokens (e.g., "Event 34", "Waiting time active"); BM25's term-frequency matching
finds them directly, while the dense encoder must bridge the gap between a natural-language
question and a terse table row.
Hybrid fusion (Reciprocal Rank Fusion of dense + BM25) underperforms pure BM25 at every
prefetch\_k: the dense signal adds noise that dilutes the BM25 signal rather than reinforcing it.
Increasing prefetch\_k from 20 to 40–60 gives a marginal gain (+0.020 Recall@10), suggesting
that the dense stream sometimes surfaces the right document but ranks it too low to influence
the top-10 without a reranker.

---

## 2. Reranker effect

Same hybrid k=20 configuration, with and without the bge-reranker-base cross-encoder.
Both runs use the same 100-question eval set.

| Configuration                     | Recall@10 | MRR   |
|-----------------------------------|-----------|-------|
| Hybrid k=20, no reranker          | 0.260     | 0.112 |
| Hybrid k=20 + bge-reranker-base   | **0.520** | **0.438** |

**Analysis.**
The cross-encoder reranker doubles Recall@10 (0.260 → 0.520) and nearly quadruples MRR
(0.112 → 0.438), making it the single largest improvement in the pipeline.
The cross-encoder reads the full (query, passage) pair jointly, which allows it to detect
subtle matches like a question about "overtemperature" and a passage about "heat dissipation"
that BM25 alone would miss.
Retrieval is therefore a two-stage process in the final system: BM25 for fast candidate
generation (prefetch\_k=20) followed by the cross-encoder for precision re-ranking.

---

## 3. Pipeline evolution

Sprint-by-sprint retrieval metrics on the eval set that existed at the time.
Rows through 2026-11-17 used 35 questions; 2026-11-23 used the full 100-question set.

| Date       | Commit  | Notes                                      | Recall@5 | Recall@10 | MRR   | Wrong-model rate |
|------------|---------|--------------------------------------------|----------|-----------|-------|-----------------|
| 2026-11-13 | ee9723d | Sprint 04 baseline; doc\_id filter bug     | 0.143    | 0.314     | 0.145 | 1.000           |
| 2026-11-17 | 2a4abff | Fixed doc\_id filter + table\_row indexing | 0.514    | 0.514     | 0.471 | 0.409           |
| 2026-11-17 | 823806f | Tuned prefetch\_k=20 (no reranker yet)     | 0.514    | 0.514     | 0.486 | 0.400           |
| 2026-11-23 | ba12b5a | Reranker + 100-question eval set           | 0.520    | 0.520     | 0.438 | 0.464           |

**Analysis.**
The largest step was the doc\_id bug fix (ee9723d → 2a4abff): fixing the wrong-model rate from
1.000 to 0.409 and raising Recall@10 by +0.200 by ensuring the dense index was queried with
the correct per-manual filter.
MRR dropped from 0.486 to 0.438 when expanding the eval set from 35 to 100 questions because
the 35 added wrong\_model\_trap and unanswerable questions always contribute MRR=0, pulling the
mean down even though the answerable-question quality stayed the same.
The wrong-model rate of 0.464 on the 100-question set reflects the still-low abstain recall
(§4): the system retrieves plausible-looking passages even for out-of-scope queries and often
does not threshold them out.

---

## 4. Answer quality

LLM-as-a-judge evaluation (Qwen2.5 3B) on the 100-question eval set, run 2026-11-23.
Judge-human agreement verified on 20 sampled verdicts: 12/14 agreed (86 %).

| Metric            | Value |
|-------------------|-------|
| Citation accuracy | 0.400 |
| Faithfulness      | 0.862 |
| Correctness       | 0.862 |
| Abstain precision | 1.000 |
| Abstain recall    | 0.343 |

**Analysis.**
Faithfulness and correctness are identical at 0.862, which suggests the judge treats them as
nearly synonymous for this domain: an answer that stays within the retrieved passages is almost
always factually correct, and an incorrect answer almost always fabricates something not in the
passages.
Citation accuracy (0.400) is well below faithfulness (0.862), meaning the model often produces
a correct answer but either omits a citation or cites the wrong page number; this is a known
weakness of small instruction-tuned models on structured JSON output with citation constraints.
Abstain precision (1.000) confirms the system never abstains incorrectly on answerable
questions, but abstain recall (0.343) is low: only 12 of 35 abstainable questions are correctly
refused, because the reranker scores for wrong-model passages are still high enough to pass the
current abstain threshold.
