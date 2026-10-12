---
name: sprint-planning
description: Run Monday sprint planning against Vikunja - pick stories for the sprint, set the goal and due dates, log it. Use when Natalia says to plan or start a sprint.
---

# Sprint planning

1. Work out the sprint number: the highest `sprint:NN` label that still has open stories, or the next one if the last sprint was closed at review.
2. From Vikunja, list:
   - open stories labelled with this sprint
   - stories carried over from earlier sprints (open, older sprint label)
   - velocity: points done in each of the last three sprints, from `docs/sprint-log.md`
3. Propose the sprint to Natalia in Portuguese:
   - the sprint goal, one sentence, from the backlog plan
   - the stories, with points and total, carry-overs first
   - a warning if the total is above recent velocity, with which story to move out
   - a short study plan for the week: the Study topics of the sprint's stories, in the order the stories will be done, with one or two sources each
4. Wait for her yes or changes. Then:
   - relabel carried-over stories to this sprint
   - set every sprint story's due date to this Friday
   - leave status labels off until work starts
5. Append to `docs/sprint-log.md` (newest first):
   ```
   ## Sprint NN · planning · YYYY-MM-DD
   Goal: ...
   Committed: N pts (ids)
   Carried over: ids or none
   ```
