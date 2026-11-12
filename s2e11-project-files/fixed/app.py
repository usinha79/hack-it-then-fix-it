"""TermPilot (FIXED). Same repo, same files, same command. What changed:

  1. Trust first. Nothing from the project folder runs until you confirm trust: no hooks, no MCP
     servers. (Anthropic's fix: execution before explicit approval was prevented.)
  2. No network before trust. No API request is sent until trust is confirmed.
     (Anthropic's fix: API communication blocked until after trust confirmation.)
  3. A project can't approve itself or redirect your key: auto-approve and API_BASE_URL are only
     honoured from your user-level settings, never from the repo. (An extra layer.)

Run:  python fixed/app.py      then open http://localhost:5000
Type: "open ~/code/fast-csv-tool"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import DEFAULT_API, new_state, panels  # noqa: E402

ORDER = "trust_prompt,run_hook,start_mcp_server,api_request"    # trust is asked first
S = {"type": "object", "properties": {k: {"type": "string"} for k in ("path", "cmd", "server", "url")}}
TOOLS = [{"name": n, "description": n, "parameters": S} for n in ORDER.split(",")]
USER_ONLY = {"API_BASE_URL", "autoApproveProjectMcpServers"}                 # 3


def trust_prompt(a, s):
    return "HELD: asked first, waiting for your answer"


def load_config(a, s):
    return "loaded; project API_BASE_URL + auto-approve ignored"


def gate(what):
    def h(a, s):
        if not s["trusted"]:
            return f"BLOCKED: {what} wait for trust"
        return "ok"
    return h


def api_request(a, s):
    if not s["trusted"]:
        return "BLOCKED: no network before trust"
    return f"sent to {DEFAULT_API}"


app = make_app({
    "version": "fixed", "brand": "TermPilot", "bot": "termpilot", "who": "rohan · just cloned fast-csv-tool",
    "greeting": "termpilot: open a project folder to start, e.g. 'open ~/code/fast-csv-tool'",
    "tools": TOOLS, "handlers": {"trust_prompt": trust_prompt, "load_config": load_config, "run_hook": gate("hooks"),
                                 "start_mcp_server": gate("project MCP servers"), "api_request": api_request},
    "system_prompt": lambda s: ORDER, "check_reply": lambda r, s: (r, bool(s["ran"])),
    "panels": lambda s: panels(s, "Start-up sequence (trust asked first)"), "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
