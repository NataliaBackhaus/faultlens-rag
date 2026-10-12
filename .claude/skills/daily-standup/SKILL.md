---
name: daily-standup
description: Daily standup - compare git activity with Vikunja, update story checklists and status labels, flag blockers. Use when Natalia says standup, daily, or asks what to do today.
---

# Daily standup

1. Read `git log --since="yesterday" --oneline` and `git status`.
2. From Vikunja, list this sprint's stories with their checklists and status labels.
3. Match commits to story tasks. For each clear match, tick the checklist item. If unsure, ask instead of ticking.
4. Update status labels: add `status:doing` to stories with new work; never mark a story done unless every Definition of Done item in CLAUDE.md is met.
5. Tell Natalia in Portuguese, in at most six lines:
   - what moved since yesterday
   - what to do today (the next unticked task of the highest-priority open story), and, if that story is just starting, what to read first from its Study section
   - any blocker, and whether the sprint goal is still on track (points done versus days left)
6. Append one line to `docs/sprint-log.md` only if something changed: `- YYYY-MM-DD: <what moved>; blockers: <none or what>`.
