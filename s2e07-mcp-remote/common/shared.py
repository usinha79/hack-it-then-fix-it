"""Shared pieces for the mcp-remote lab: a remote MCP server that asks you to log in, the bridge's
"open the login page" step, a fake Windows laptop, and the side panels.

Story: AppBridge connects a desktop AI app to remote MCP servers (modelled on mcp-remote). When a
server answers 401, the bridge reads the server's OAuth metadata and opens its
authorization_endpoint in your browser so you can log in. Before 0.1.16, mcp-remote passed that URL,
which the server controls, to the `open` package. On Windows, `open` launches the browser through
PowerShell, and PowerShell evaluates $( ... ) inside the string. JFrog (CVE-2025-6514, CVSS 9.6,
July 2025) showed a malicious server can run any command on the client this way.

SAFETY: nothing in this lab runs a real command. PowerShell is simulated: every $( ... ) it would
evaluate is only looked up in a file of fake outputs and logged.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVERS = json.load(open(os.path.join(ROOT, "logs", "servers.json")))
FAKE_OUTPUT = json.load(open(os.path.join(ROOT, "logs", "laptop.json")))


def new_state():
    return {"ran": [], "server": None}


def connect_server(args, state):
    host = args["server"].replace("https://", "").replace("http://", "").strip("/")
    s = SERVERS[host]
    state["server"] = host
    return (f"{s['status']} login required. OAuth metadata from {host}:\n" + json.dumps(s["oauth_metadata"], indent=1))


def simulated_powershell(command_line, state):
    """Stands in for PowerShell. Like the real thing, it evaluates every $( ... ) subexpression inside
    a double-quoted string before running the command. Here 'running' means logging a fake output."""
    for sub in re.findall(r"\$\(([^)]*)\)", command_line):
        out = FAKE_OUTPUT.get(sub, "(lab) command logged, nothing executed")
        state["ran"].append({"head": f"PS> {sub}", "body": out[:64], "status": "leak"})
    return "browser launched"


def open_with_shell(url, state):
    """How `open` launched a URL on Windows: build a PowerShell command line around the string."""
    cmd = f'powershell -NoProfile -Command Start "{url}"'
    simulated_powershell(cmd, state)
    return cmd


def panels(state, requests_panel):
    meta = SERVERS["toolshub.example"]["oauth_metadata"]
    srv = [{"head": "toolshub.example  ·  401 login required", "status": "warn"},
           {"head": "authorization_endpoint (chosen by the server)", "body": meta["authorization_endpoint"], "status": "warn"}]
    return [{"id": "server", "title": "Remote MCP server (anyone can run one)", "kind": "items", "fit": True,
             "items": srv if state["server"] else [], "empty": "Not connected."},
            {**requests_panel, "fit": True},
            {"id": "ran", "title": "Commands run on this laptop (Windows)", "kind": "items", "fit": True,
             "items": state["ran"], "empty": "No commands run."}]


def steps_panel(state, ok_status="executed"):
    items = []
    for c in state["calls"]:
        if c["name"] == "connect_server":
            items.append({"head": f"connect {c['arguments']['server']}", "body": "→ 401, read OAuth metadata", "status": "ran"})
        else:
            res = " ".join(c["result"].split())
            items.append({"head": "open login page", "body": "→ " + (res if len(res) < 150 else res[:147] + "..."),
                          "status": "blocked" if c["status"] == "blocked" else ok_status})
    return {"id": "calls", "title": "What the bridge did to open the login page", "kind": "items", "items": items,
            "empty": "Nothing yet."}
