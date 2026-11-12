# Season 2 · Ep 9 — Zero-click MCP: my AI editor ran a stranger's command

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the zero-click pattern from **OX Security**'s April 2026 research on MCP's STDIO transport,
in particular **CVE-2026-30615** in the **Windsurf** editor: a prompt injection could add a server to
the editor's MCP config, and the editor launched it with no click. OX said Windsurf was the only
editor they tested where no user step was needed. Everything here runs locally with fake data.
**No command is ever executed:** the config is a Python dict and the launch is simulated.

An STDIO MCP server is just a command your app launches. So whoever can edit the server list can
run code. **CodeWave** is an AI code editor. The developer asks its agent to summarise a blog post.
A hidden `<div>` on the page tells the assistant to add a `docs-helper` server to
`~/.codewave/mcp.json` whose command is `sh -c "whoami; cat ~/.ssh/id_ed25519"`. The agent writes
the config, the editor sees a new server and starts it.

| | Vulnerable | Fixed |
|---|---|---|
| MCP config | the agent can write it | protected: changes are HELD until the developer approves outside the chat |
| New servers | auto-start | never auto-start: the full command is shown and waits for a click |
| Server command | anything, including a shell | pinned, allowlisted binaries by full path, no shell (a layer: OX showed allowlists alone can be bypassed through arguments) |
| Result | shell one-liner runs, SSH key read | same page, same agent, nothing runs |

The model falls for the page in **both** versions. The fix does not depend on the model saying no.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Summarise mcp-tips.example/new-servers"**. The page is in `web/new-servers.html`.

## The defences

1. **Protect the MCP config.** Agents can propose changes; a human approves them outside the chat.
2. **No auto-start.** Show the full command of any new server and wait for a click.
3. **Pinned commands.** Allowlisted binaries by full path, never a shell. A layer, not the fix.

And: open your editor's MCP config today and check every command in it. Keep your AI editor updated.

Maps to **OWASP LLM01 Prompt Injection**, **LLM03 Excessive Agency** (2026) and **ASI05 Unexpected Code Execution** (Agentic Top 10, 2026).

Real-world reference: OX Security, MCP STDIO research, April 2026 (CVE-2026-30615, Windsurf).

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
