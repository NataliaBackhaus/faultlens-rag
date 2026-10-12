---
name: backlog-import
description: One-time import of backlog/backlog.yaml into the Vikunja project as labelled tasks. Use when setting up Vikunja or when new stories are added to the YAML.
---

# Import the backlog into Vikunja

1. Read `backlog/backlog.yaml` and the label scheme in CLAUDE.md.
2. Find the Vikunja project "FaultLens RAG"; create it if it does not exist.
3. Create any missing labels: `epic:E1`..`epic:E15`, `pts:1`, `pts:2`, `pts:3`, `pts:5`, `pts:8`, `sprint:00`..`sprint:10`, `status:doing`, `status:review`, `status:blocked`, `stretch`.
4. List existing tasks in the project. A story already exists when a task title starts with its id followed by a space; skip those, so the import can run again safely.
5. For each missing story, create a task:
   - Title: `<id> <title>`
   - Description, in Markdown:
     ```
     **Story:** <story>

     **Done when:** <done_when>

     - [ ] <task 1>
     - [ ] <task 2>

     **Study**
     - <topic 1>
       - <source>
       - <source>
     ```
     Leave the Study section out when the story has no `study` field. Keep every source URL exactly as written.
   - Labels: its epic, points and sprint labels, plus `stretch` if `stretch: true`.
   - Due date: leave empty; sprint planning sets it.
6. Report: stories created, skipped, and any that failed. Show points per sprint so Natalia can check they match the plan (about 12 a sprint).

Do not create more than 15 tasks per call; work in batches and continue until all are done.
