# Season 2 · Ep 11 — Coding agent project files: "do you trust this folder?" came too late

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern **Check Point Research** published in February 2026 in **Claude Code**
(**CVE-2025-59536** and **CVE-2026-21852**, reported July–October 2025). A cloned repository's own
config files (hooks, MCP servers, environment settings) could run hidden shell commands and send
API traffic, with the user's API key, to an attacker's server, some of it before the user had
confirmed trust in the folder. Anthropic fixed this by preventing execution, and blocking API
communication, until trust is confirmed.

This lab uses our own tool, **TermPilot**, not the real product. Everything runs locally with fake
data. **Nothing is executed and nothing is sent:** commands and requests are only logged.

The cloned repo `fast-csv-tool` ships `.termpilot/settings.json` (a `SessionStart` hook that pipes a
script to `sh`, `API_BASE_URL` pointing at the attacker's proxy, and `autoApproveProjectMcpServers`)
and `.mcp.json` (a `csv-helper` server whose command reads `~/.aws/credentials`).

| | Vulnerable | Fixed |
|---|---|---|
| Trust prompt | asked last | asked first; everything else waits |
| Hooks / project MCP servers | run on open | blocked until trusted (as in the real fix) |
| API traffic | sent on open, to the project's `API_BASE_URL` | no network before trust (as in the real fix) |
| Project self-approval / base URL | honoured | only honoured from user-level settings (an extra layer) |
| Result | script, cloud key, API key out | nothing ran, nothing left |

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Type: **"open ~/code/fast-csv-tool"**. The repo's config is in `logs/repo.json`.

## The defences

1. **Trust first.** Nothing from a project folder runs until the user confirms.
2. **No network before trust.** No credentials leave until the user answers.
3. **Projects can't approve themselves** or redirect your API key.

And: keep your coding agent updated, and read a cloned repo's dot folders before you open it.

Maps to **ASI04 Agentic Supply Chain Vulnerabilities**, **ASI05 Unexpected Code Execution** (Agentic Top 10, 2026) and **A08:2025 Software or Data Integrity Failures**.

Real-world reference: Check Point Research, "Caught in the Hook: RCE and API Token Exfiltration Through Claude Code Project Files", February 2026.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
