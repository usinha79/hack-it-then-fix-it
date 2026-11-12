# Season 2 · Ep 7 — mcp-remote: "please log in" ran commands on my laptop

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind **CVE-2025-6514** (CVSS 9.6) in **mcp-remote**, disclosed by **JFrog**
in July 2025. Affected 0.0.5 to 0.1.15; fixed in 0.1.16. Everything here runs locally against a
lab app with fake data. **No command is ever executed:** PowerShell is simulated, and every
`$( ... )` it would evaluate is only looked up in a file of fake outputs and logged.

**AppBridge** connects a desktop AI app to remote MCP servers, like mcp-remote does. When a server
answers 401, the bridge reads the server's OAuth metadata and opens `authorization_endpoint` in
your browser so you can log in. The server chooses that URL. On Windows, the `open` helper launches
the browser through PowerShell, and PowerShell evaluates `$( ... )` inside the string first. So a
hostile server's "login page" runs commands on your laptop before you type anything.

| | Vulnerable | Fixed |
|---|---|---|
| Login URL | used as the server sent it | `sanitize_url`: http(s) only, suspicious hostnames rejected (as in 0.1.16) |
| Encoding | none | every part percent-encoded: `$(whoami)` becomes `%24(whoami)` (as in 0.1.16) |
| Launch | PowerShell command string | argument list, no shell (an extra layer) |
| Result | 2 commands run as the developer | same server, same metadata, nothing runs |

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Connect to the MCP server at toolshub.example"**. Watch "What the bridge did to open the
login page" and "Commands run on this laptop". The hostile metadata is in `logs/servers.json`.

## The defences

1. **Scheme allowlist.** Only open `http`/`https` URLs.
2. **Encode every part** of a URL that came from someone else before it reaches the OS.
3. **No shell.** Launch programs with argument lists, never command strings.

And: update mcp-remote to 0.1.16 or later, and only connect to MCP servers you trust, over HTTPS.

Maps to **OWASP A05:2025 Injection** and **ASI04 Agentic Supply Chain Vulnerabilities** (Agentic Top 10, 2026).

Real-world reference: JFrog Security Research, "Critical RCE Vulnerability in mcp-remote: CVE-2025-6514", July 2025.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
