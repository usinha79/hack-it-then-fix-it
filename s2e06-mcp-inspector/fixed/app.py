"""ToolScope (FIXED). Same tool, same page, same browser. What changed, as in MCP Inspector 0.14.1:

  1. A session token. The proxy prints a random token at start-up; every request must carry it
     (X-MCP-Proxy-Auth: Bearer <token>). A web page can't know it, so its requests fail.
  2. Origin checks. Only ToolScope's own UI origin may call the proxy. Another site's page is refused.
  3. Host checks. Requests must be addressed to localhost or 127.0.0.1, which stops DNS rebinding
     and requests addressed to 0.0.0.0.

Run:  python fixed/app.py      then open http://localhost:5000
Type: mcp-tips.example/setup-guide
"""
import os
import sys

from flask import request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import new_state, panels, proxy_sse, requests_panel, visit  # noqa: E402

POLICY = {"origins": {"http://localhost:6274", "http://127.0.0.1:6274"},   # ToolScope's own UI
          "hosts": {"localhost", "127.0.0.1"}}

TOOLS = [{"name": "visit", "description": "Load a web page.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}},
         {"name": "page_fetch", "description": "A request the page's script sends.", "parameters": {"type": "object", "properties": {
             "url": {"type": "string"}, "origin": {"type": "string"}}}}]


def page_fetch(args, state):
    code, text = proxy_sse(args["url"], {"Origin": args["origin"]}, state, POLICY)
    return text


def proxy_items(state):
    return [{"head": f"Session token required (Bearer {state['token'][:6]}…)", "status": "ok"},
            {"head": "Origin allowlist: ToolScope's own UI only", "status": "ok"},
            {"head": "Host allowlist: localhost, 127.0.0.1", "status": "ok"}]


def routes(app, state):
    print(f"[fixed] proxy session token: {state['token']}", flush=True)

    @app.get("/sse")
    def sse():
        code, text = proxy_sse(request.url, request.headers, state, POLICY)
        return text, code or 502


app = make_app({
    "version": "fixed", "brand": "ToolScope", "bot": "Browser", "who": "rohan's laptop (proxy: token + origin checks)",
    "greeting": "This is the developer's browser. Type a web address to open it.",
    "tools": TOOLS, "handlers": {"visit": visit, "page_fetch": page_fetch},
    "system_prompt": lambda s: "", "check_reply": lambda r, s: (r, bool(s["ran"])),
    "panels": lambda s: panels(s, requests_panel(s), proxy_items(s)),
    "new_state": new_state, "extra_routes": routes,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
