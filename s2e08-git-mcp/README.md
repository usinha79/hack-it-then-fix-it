# Season 2 · Ep 8 — Git MCP server: a README that ran code

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the chain **Cyata** disclosed in January 2026 in **mcp-server-git**, the official Git MCP
server: **CVE-2025-68143** (git_init on any path), **CVE-2025-68145** (repo_path not checked against
`--repository`) and **CVE-2025-68144** (argument injection in git_diff). Fixed in 2025.9.25 and
2025.12.18. Combined with the Filesystem MCP server and prompt injection, they led to code execution.
Everything here runs locally with fake data. **No command is ever executed:** the disk is a Python
dict, Git is simulated, and the filter command is only looked up in a file of fake outputs.

**DevPilot** is a coding agent with two MCP servers: Git (`--repository ~/projects/widget-demo`) and
Filesystem (`~/projects`). The developer asks it to set up a project from its README. An HTML
comment in the README tells AI agents to: `git_init` a repo in `~/projects/scratch`, write a
`.git/config` with a **clean filter** (a command Git runs on files you stage), a `.gitattributes`
that turns it on, and the script, then `git_add`. Staging the file runs the script.

| | Vulnerable | Fixed |
|---|---|---|
| `git_init` | creates a repo anywhere | removed (as in the real fix) |
| `repo_path` | any path accepted | resolved, must be inside `--repository` (as in the real fix) |
| Filesystem writes | anywhere under `~/projects`, including `.git/` | `.git/` is off-limits (an extra layer) |
| Result | script runs, SSH key read | same agent, same README, nothing runs |

The model falls for the README in **both** versions. The fix does not depend on the model saying no.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Set up widget-demo from its README."** The README is in `logs/project.json`.

## The defences

1. **Remove tools the agent doesn't need** (here: `git_init`).
2. **Resolve and check every path** against the scope the server was configured with.
3. **Keep agents out of `.git/`**: config, hooks and filters decide what Git executes.

And: update mcp-server-git to 2025.12.18 or later, and check which MCP servers your agent has *together*.

Maps to **OWASP LLM01 Prompt Injection**, **LLM03 Excessive Agency** (2026) and **ASI05 Unexpected Code Execution** (Agentic Top 10, 2026).

Real-world reference: Cyata, "How We Found Code Execution in Anthropic's Official Git MCP Server", January 2026.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
