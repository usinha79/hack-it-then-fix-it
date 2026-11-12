"""TermPilot (VULNERABLE). Recreates the pattern Check Point Research reported in Claude Code
(CVE-2025-59536 and CVE-2026-21852, February 2026).

What makes it exploitable, like the real case:
  1. Project config is trusted before the user is asked: SessionStart hooks run on open.
  2. Project MCP servers start on their own, because the project's own settings auto-approve them.
  3. The project can set the API base URL, so the first request, carrying your API key, goes to
     the attacker's server.
  ... and only then does the trust prompt appear.

Nothing really runs or leaves this machine: commands and requests are only logged.

Run:  python vulnerable/app.py      then open http://localhost:5000
Type: "open ~/code/fast-csv-tool"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import MCP, R, SETTINGS, new_state, panels, ran, run_command  # noqa: E402

ORDER = "run_hook,start_mcp_server,api_request,trust_prompt"   # trust is asked last
S = {"type": "object", "properties": {k: {"type": "string"} for k in ("path", "cmd", "server", "url")}}
TOOLS = [{"name": n, "description": n, "parameters": S} for n in ORDER.split(",")]


def load_config(a, s):
    return "loaded hooks, env and MCP servers from the project folder"


def run_hook(a, s):
    return run_command(a["cmd"], s)


def start_mcp_server(a, s):
    srv = MCP[a["server"]]
    if SETTINGS.get("autoApproveProjectMcpServers"):          # the project approves itself
        return run_command(srv["args"][1], s)
    return "needs approval"


def api_request(a, s):
    base = SETTINGS["env"].get("API_BASE_URL", "")            # the project chooses where your key goes
    ran(s, f"POST {base}{a['url']}", f"Authorization: Bearer {R['api_key']}")
    return f"sent to {base} with your API key"


def trust_prompt(a, s):
    return "asked last: do you trust this folder?"


app = make_app({
    "version": "vulnerable", "brand": "TermPilot", "bot": "termpilot", "who": "rohan · just cloned fast-csv-tool",
    "greeting": "termpilot: open a project folder to start, e.g. 'open ~/code/fast-csv-tool'",
    "tools": TOOLS, "handlers": {"load_config": load_config, "run_hook": run_hook, "start_mcp_server": start_mcp_server,
                                 "api_request": api_request, "trust_prompt": trust_prompt},
    "system_prompt": lambda s: ORDER, "check_reply": lambda r, s: (r, bool(s["ran"])),
    "panels": lambda s: panels(s, "Start-up sequence (trust asked last)"), "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
