# Sprint log

Newest entry first. Claude appends one entry per ceremony.

## Sprint 05 · planning · 2026-11-17
Goal: Figuras indexadas, retrieval afinado e primeira resposta ancorada no manual.
Committed: 18 pts (8.3, 8.4, 6.2, 9.1, 9.2)
Carried over: none
Due: 2026-11-21

## Sprint 04 · review and retro · 2026-11-14
Goal: Chunking, eval set and hybrid retrieval — structured chunks, seed questions and query understanding.
Committed: 13 pts · Done: 18 pts (pulled in 8.2 + 10.2 mid-sprint) · Carry-over: none
CI: 178 tests, 0 failures.
Metrics (first run, no prior sprint to compare): recall@5 0.143, recall@10 0.314, MRR 0.145, wrong_model_rate 1.0 ⚠️
Went well: programação correu bem; sprint mais forte até agora — 18 pts vs 13 comprometidos.
To improve: métricas estão estranhas; wrong_model_rate=1.0 indica incompatibilidade de formato entre questions.jsonl e payload do Qdrant.
Next sprint changes: corrigir table_row indexing no chunk_document e incompatibilidade de formato de modelo nas métricas.
Observer note: velocidade em alta (9→13→5→13→18); baseline de métricas estabelecido mas requer correção antes de ser confiável.

## Sprint 04 · planning · 2026-11-09
Goal: Chunking, eval set and hybrid retrieval — structured chunks, seed questions and query understanding.
Committed: 13 pts (7.1, 10.1, 7.2, 8.1)
Carried over: 7.1, 10.1 (from sprint:03)
Due: 2026-11-14

## Sprint 03 · review and retro · 2026-11-09
Goal: Structured extraction — error-code rows, device metadata, model aliases and figure crops.
Committed: 13 pts · Done: 13 pts · Carry-over: none
CI: 92 tests, 0 failures.
Metrics: n/a (eval set not yet created)
Went well: all 4 stories completed with 4 days to spare; velocity fully recovered from sprint 02.
To improve: none identified.
Next sprint changes: none.
Observer note: sprint finished early — Natalia freed time for personal commitments mid-week.

## Sprint 03 · planning · 2026-11-02
Goal: Structured extraction — error-code rows, device metadata, model aliases and figure crops.
Committed: 13 pts (4.1, 5.1, 5.2, 6.1)
Carried over: 4.1, 5.1 (from sprint:02)
Due: 2026-11-07

## Sprint 02 · 3.4 region classification accuracy · 2026-10-27
Sample: 50 elements across 3 manuals (seed=42). Correct: 50/50. Accuracy: 100%.

## Sprint 02 · review and retro · 2026-11-02
Goal: Clean ingestion — classify regions, flag quality issues, extract error-code rows and device metadata.
Committed: 13 pts · Done: 5 pts · Carried over: 4.1, 5.1
Metrics: n/a (eval set not yet created)
Went well: both completed stories passed DoD on first check; classifier reached 100% accuracy on 50-element sample.
To improve: illness reduced available time; OCR currently applied to the full document rather than flagged pages only (Docling has no per-page OCR API).
Next sprint changes: none requested.

## Sprint 02 · planning · 2026-10-26
Goal: Clean ingestion — classify regions, flag quality issues, extract error-code rows and device metadata.
Committed: 13 pts (3.4, 3.5, 4.1, 5.1)
Carried over: 3.4 (from sprint:01)
Due: 2026-10-31

## Sprint 01 · review and retro · 2026-10-24
Goal: First end-to-end RAG path — download manuals, render pages, parse with Docling, answer one error-code question.
Committed: 13 pts · Done: 13 pts · Carried over: none
Metrics: n/a (eval set not yet created)
Went well: wrote most scripts independently; understood library internals without guidance.
To improve: Docling documentation is hard to navigate — used source code exploration instead. Personal commitments reduced available time mid-sprint.
Next sprint changes: none requested.

## Sprint 01 · planning · 2026-10-20
Goal: First end-to-end RAG path — download manuals, render pages, parse with Docling, answer one error-code question.
Committed: 13 pts (2.1, 3.1, 3.2, 3.3)
Carried over: 2.1 (from sprint:00)
Due: 2026-10-24

## Sprint 00 · review and retro · 2026-10-20
Goal: Repo, local models, CI and the manual list.
Committed: 12 pts · Done: 9 pts · Carried over: 2.1
Metrics: n/a (eval set not yet created)
Went well: task organisation was clear; all four done stories passed DoD on first check.
To improve: fear of writing code delayed starting the last story.
Next sprint changes: Natalia will write more code herself; 2.1 carry-over is first priority.

## Sprint 00 · planning · 2026-10-09
Goal: Repo, local models, CI and the manual list.
Committed: 12 pts (1.1, 1.2, 1.3, 1.4, 2.1)
Carried over: none
Due: 2026-10-17

<!-- Template
## Sprint NN · review and retro · YYYY-MM-DD
Goal: ...
Committed: N pts · Done: N pts · Carried over: ids
Metrics: recall@10 ..., MRR ..., citation accuracy ...
Went well: ...
To improve: ...
Next sprint changes: ...
-->
