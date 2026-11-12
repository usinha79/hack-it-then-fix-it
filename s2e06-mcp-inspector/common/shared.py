"""Shared pieces for the MCP Inspector lab: a local MCP debugging proxy, a fake laptop, the
"internet" page that attacks it, and the side panels.

Story: a developer runs ToolScope, a local debugging tool for MCP servers (modelled on MCP
Inspector). Its proxy can launch an MCP server for you: give it a command and it starts that
process over stdio. Before version 0.14.1, MCP Inspector's proxy did that with no authentication
and no check of where the request came from. Oligo Security showed (CVE-2025-49596, CVSS 9.4,
June 2025) that any web page the developer opens can send that request from the browser, using
the "0.0.0.0-day" browser behaviour or DNS rebinding, and run commands on the laptop.

SAFETY: nothing in this lab runs a real command. The "laptop" is a dictionary of fake outputs,
and every command the proxy accepts is only written to a log.
"""
import json
import os
import re
import secrets
from urllib.parse import parse_qs, urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAKE_OUTPUT = json.load(open(os.path.join(ROOT, "logs", "laptop.json")))


def new_state():
    return {"ran": [], "token": secrets.token_hex(16)}


def fake_run(cmd):
    """Never executes anything: returns the lab's canned output for a command."""
    return FAKE_OUTPUT.get(cmd, "(lab) command logged, nothing executed")


def proxy_sse(url, headers, state, policy):
    """The proxy's /sse endpoint. policy = None (vulnerable) or a dict with the fixed checks.
    Returns (http_status, text)."""
    q = parse_qs(urlparse(url).query)
    host = urlparse(url).hostname
    origin = headers.get("Origin", "")
    if policy:
        fails = []
        if headers.get("X-MCP-Proxy-Auth") != f"Bearer {state['token']}":
            fails.append("401 no session token")
        if origin and origin not in policy["origins"]:
            fails.append(f"origin {origin} not allowed")
        if host not in policy["hosts"]:
            fails.append(f"host {host} not allowed")
        if fails:
            return 401 if fails[0].startswith("401") else 403, "BLOCKED: " + ", ".join(fails)
    if q.get("transportType", [""])[0] != "stdio":
        return 400, "unsupported transport"
    cmd = " ".join(q.get("command", []) + q.get("args", []))
    out = fake_run(cmd)
    state["ran"].append({"head": f"$ {cmd}", "body": out.split("\n")[0][:64], "status": "leak",
                         "origin": origin or "(none)"})
    return 200, f"spawned stdio server: {cmd}\n{out}"


def visit(args, state):
    """The browser loads a page from the lab's fake internet (web/)."""
    name = urlparse(args["url"]).path.strip("/").split("/")[-1] or "index"
    html = open(os.path.join(ROOT, "web", name + ".html")).read()
    return html


def page_fetches(html):
    """The fetch() calls inside a page's <script>: what the browser will send on the page's behalf."""
    return re.findall(r"fetch\(\"([^\"]+)\"", html)


def panels(state, calls_panel, proxy_items):
    return [{"id": "proxy", "title": "ToolScope proxy on this laptop", "kind": "items", "fit": True, "items": proxy_items},
            {**calls_panel, "fit": True},
            {"id": "ran", "title": "Commands run on this laptop", "kind": "items", "fit": True,
             "items": state["ran"], "empty": "No commands run."}]


def requests_panel(state):
    """Every request the page's script sent, and what the proxy did with it."""
    items = []
    for c in state["calls"]:
        if c["name"] == "visit":
            items.append({"head": f"GET {c['arguments']['url']}", "body": "→ page loaded, its script runs", "status": "ran"})
            continue
        u = urlparse(c["arguments"]["url"])
        res = " ".join(c["result"].split())
        items.append({"head": f"GET {u.netloc}{u.path}?{u.query}"[:80],
                      "body": f"Origin: {c['arguments']['origin']}  → " + (res if len(res) < 56 else res[:53] + "..."),
                      "status": "blocked" if c["status"] == "blocked" else "executed"})
    return {"id": "calls", "title": "Requests from this laptop's browser", "kind": "items", "items": items,
            "empty": "No requests yet."}
