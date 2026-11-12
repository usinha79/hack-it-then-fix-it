"""ToolScope (VULNERABLE). Recreates CVE-2025-49596 in MCP Inspector before 0.14.1 (Oligo Security, June 2025).

ToolScope is a local debugging tool for MCP servers. Its proxy (port 6277) can start an MCP server
for you: /sse?transportType=stdio&command=...&args=... launches that command over stdio.

What makes it exploitable, like the real case:
  1. The proxy has no authentication: any request that reaches it is obeyed.
  2. It doesn't check Origin or Host, so a request sent by some other website's page is accepted.
  3. Browsers let public pages send requests to 0.0.0.0, which reaches services on the visitor's
     own machine (the "0.0.0.0-day"; DNS rebinding works too). The page can't read the answer,
     but it doesn't need to: the command already ran.

Nothing is really executed in this lab: commands are logged against fake outputs.

Run:  python vulnerable/app.py      then open http://localhost:5000
Type: mcp-tips.example/setup-guide
Try:  curl 'http://localhost:5000/sse?transportType=stdio&command=id' -H 'Origin: https://mcp-tips.example'
"""
import os
import sys

from flask import request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import new_state, panels, proxy_sse, requests_panel, visit  # noqa: E402

POLICY = None  # no token, no Origin check, no Host check

TOOLS = [{"name": "visit", "description": "Load a web page.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}},
         {"name": "page_fetch", "description": "A request the page's script sends.", "parameters": {"type": "object", "properties": {
             "url": {"type": "string"}, "origin": {"type": "string"}}}}]


def page_fetch(args, state):
    code, text = proxy_sse(args["url"], {"Origin": args["origin"]}, state, POLICY)
    return text


def proxy_items(state):
    return [{"head": "Listening on 0.0.0.0:6277", "status": "warn"},
            {"head": "Authentication: none", "status": "warn"},
            {"head": "Origin / Host checks: none", "status": "warn"}]


def routes(app, state):
    @app.get("/sse")
    def sse():  # the real HTTP endpoint, for hands-on testing with curl
        code, text = proxy_sse(request.url, request.headers, state, POLICY)
        return text, code or 502


app = make_app({
    "version": "vulnerable", "brand": "ToolScope", "bot": "Browser", "who": "rohan's laptop",
    "greeting": "This is the developer's browser. Type a web address to open it.",
    "tools": TOOLS, "handlers": {"visit": visit, "page_fetch": page_fetch},
    "system_prompt": lambda s: "", "check_reply": lambda r, s: (r, bool(s["ran"])),
    "panels": lambda s: panels(s, requests_panel(s), proxy_items(s)),
    "new_state": new_state, "extra_routes": routes,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
