---
name: sprint-review
description: Friday sprint review and retrospective - check done stories against the Definition of Done, record velocity and eval metrics, run a short retro, prepare carry-over. Use when Natalia says review, retro, or close the sprint.
---

# Sprint review and retrospective

## Review
1. List this sprint's stories from Vikunja. For each one marked done, check the Definition of Done in CLAUDE.md (CI status, tests, eval numbers, docs). Reopen any that fail and say why.
2. Compute committed points, done points and carry-over ids.
3. If `eval/history.csv` exists, show the latest metrics against last sprint's (recall@10, MRR, citation accuracy, abstain rate). Flag any drop.
4. At the end of Sprint 7 and Sprint 10, check the release gate in CLAUDE.md and propose the git tag if it passes.

## Retro
5. Ask Natalia in Portuguese three short questions: what went well, what to improve, one change for next sprint. Add your own observation from the data (velocity trend, stories that grew, blockers).

## Close
6. Leave unfinished stories open; sprint planning relabels them.
7. If velocity is below plan two sprints in a row, propose what to drop (11.3, then 13.3, then 14.1; never evaluation).
8. Append to `docs/sprint-log.md` using the template at the top of that file.
