# FaultLens RAG setup: Claude Code as PM and Scrum Master with a local Vikunja

Vikunja runs on the home network at `192.168.2.200:8082` and has a built-in MCP server (Vikunja 2.7.0 or later, see [Vikunja MCP docs](https://vikunja.io/help/mcp/)). A private address is only reachable from the same network, so run Claude Code locally (terminal CLI or desktop app), not in a Claude Code cloud session.

## 1. Put the files in the code repository

Copy everything in this folder to the root of the `faultlens-rag` repository, next to the code. Claude Code reads `CLAUDE.md` and `.claude/` from the folder you start it in.

```
repo/
  CLAUDE.md
  .claude/settings.json
  .claude/skills/{backlog-import,sprint-planning,daily-standup,sprint-review}/SKILL.md
  backlog/backlog.yaml
  docs/sprint-log.md
  ...code...
```

Append `.gitignore.append` to `.gitignore`, then delete it.

## 2. Check the Vikunja version

```
curl http://192.168.2.200:8082/api/v1/info   # "version" must be 2.7.0 or later
```

## 3. Create an MCP token

In Vikunja: Settings > MCP. Create a token; the default permission preset (tasks, projects, labels, assignees, comments, user search) is enough. Copy the token.

## 4. Add the MCP server to Claude Code

From the repository folder. Options go before the server name:

```
claude mcp add --transport http --header 'Authorization: Bearer YOUR_TOKEN' vikunja 'http://192.168.2.200:8082/api/v2/mcp'
```

This saves the server and token in your user config for this project only (local scope), so the token never lands in git.

## 5. Check the connection

Run `claude`, then `/mcp`: `vikunja` should show as connected. Ask "list my Vikunja projects" as a test.

## 6. Import the backlog

Run `/backlog-import`. It creates the project, labels and 45 stories, skipping any that already exist. Open Vikunja and check two or three stories before going on.

## 7. Start the first sprint

Run `/sprint-planning`. From then on: `/daily-standup` each working day and `/sprint-review` on Friday.

## Troubleshooting

- `/mcp` shows failed: check the URL ends in `/api/v2/mcp` and the version is 2.7.0 or later.
- 401 errors: the token expired or lacks a permission; create a new one in Settings > MCP.
- Connection refused: Vikunja is down or the machine is not on the home network.
