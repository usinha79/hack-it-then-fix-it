# Season 2 · Ep 6 — MCP Inspector: a web page ran commands on my laptop

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind **CVE-2025-49596** (CVSS 9.4) in **MCP Inspector**, the official tool
for testing MCP servers, disclosed by **Oligo Security** in June 2025 and fixed in version 0.14.1.
Everything here runs locally against a lab app with fake data. **No command is ever executed:**
the "laptop" is a file of canned outputs, and the proxy only logs what it would have run.

**ToolScope** is a local debugging tool for MCP servers. Its proxy (port 6277) can start an MCP
server for you: `/sse?transportType=stdio&command=...&args=...` launches that command. Before 0.14.1,
MCP Inspector's proxy did this with no authentication and no check of where the request came from.
The developer opens a blog post. Its script sends two requests to `0.0.0.0:6277`, which browsers
have treated as the visitor's own machine (the "0.0.0.0-day"; DNS rebinding works too). The page
can't read the answers. It doesn't need to: the commands already ran.

| | Vulnerable | Fixed (as in 0.14.1) |
|---|---|---|
| Authentication | none | random session token printed at start-up, required on every request |
| Origin | not checked | only the tool's own UI (`localhost:6274`) |
| Host | not checked | `localhost` / `127.0.0.1` only (stops DNS rebinding and `0.0.0.0`) |
| Result | 2 commands run as the developer | same page, same requests, nothing runs |

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py          # prints the proxy session token
./attack.sh                  # the exact run shown in the video
```

In the chat (the lab browser), type: **`mcp-tips.example/setup-guide`**. Watch "Requests from this
laptop's browser" and "Commands run on this laptop". The page lives in `web/setup-guide.html`.

Try the endpoint yourself:

```bash
curl 'http://localhost:5000/sse?transportType=stdio&command=id' -H 'Origin: https://mcp-tips.example'
# fixed version: add  -H "X-MCP-Proxy-Auth: Bearer <token printed at start-up>"  and drop the Origin header
```

## The defences

1. **Session token.** Any local tool that can run commands needs authentication, even if only you use it.
2. **Origin allowlist.** Refuse requests sent by other sites' pages.
3. **Host allowlist.** Accept only requests addressed to `localhost` / `127.0.0.1`.

And: update MCP Inspector to 0.14.1 or later, and know what listens on your laptop (`lsof -i -P | grep LISTEN`).

Maps to **OWASP A01:2025 Broken Access Control**, **A07:2025 Authentication Failures** and **ASI04 Agentic Supply Chain Vulnerabilities** (Agentic Top 10, 2026).

Real-world reference: Oligo Security, "Critical RCE Vulnerability in Anthropic MCP Inspector, CVE-2025-49596", June 2025.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
