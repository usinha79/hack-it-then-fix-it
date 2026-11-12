"""AppBridge (FIXED). Same server, same metadata, same flow. What changed:

  1. Scheme allowlist: only http(s) URLs may be opened (as in mcp-remote 0.1.16's sanitizeUrl).
  2. Encode every part: path, query, fragment and user info are percent-encoded, so $( ... ) becomes
     %24( ... ), plain text no shell will run (also as in 0.1.16).
  3. No shell at all: the browser is launched with an argument list, never a command string.
     (An extra layer we add; any one of these breaks the attack.)

Run:  python fixed/app.py      then open http://localhost:5000
Ask:  "Connect to the MCP server at toolshub.example"
"""
import os
import sys
from urllib.parse import parse_qsl, quote, urlsplit, urlunsplit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import connect_server, new_state, panels, steps_panel  # noqa: E402

TOOLS = [{"name": "connect_server", "description": "Connect to a remote MCP server.", "parameters": {"type": "object", "properties": {"server": {"type": "string"}}}},
         {"name": "open_login", "description": "Open the server's login page.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}}]


JS_SAFE = "()!*'~"   # what JavaScript's encodeURIComponent leaves alone


def sanitize_url(raw):
    """Port of the idea in mcp-remote 0.1.16: reject odd schemes and hostnames, encode everything else."""
    u = urlsplit(raw)
    if u.scheme not in ("http", "https"):
        raise ValueError(f"scheme {u.scheme!r} not allowed")
    host = u.hostname or ""
    if host != quote(host, safe=".-"):
        raise ValueError("suspicious hostname")
    user = quote(u.username or "", safe=JS_SAFE) + (":" + quote(u.password, safe=JS_SAFE) if u.password else "")
    netloc = (user + "@" if user else "") + host + (f":{u.port}" if u.port else "")
    path = "/" + quote(u.path[1:], safe="/" + JS_SAFE)
    query = "&".join(quote(k, safe=JS_SAFE) + "=" + quote(v, safe=JS_SAFE) for k, v in parse_qsl(u.query, keep_blank_values=True))
    return urlunsplit((u.scheme, netloc, path, query, quote(u.fragment, safe=JS_SAFE)))


def open_login(args, state):
    try:
        url = sanitize_url(args["url"])
    except ValueError as e:
        return f"BLOCKED: login URL rejected ({e})"
    argv = ["msedge.exe", url]          # an argument list: no shell ever parses the string
    return f"opened as a plain argument, no shell: {argv[1]}"


app = make_app({
    "version": "fixed", "brand": "AppBridge", "bot": "AI app", "who": "rohan (Windows laptop)",
    "greeting": "Hi! I can connect to remote MCP servers for you.",
    "tools": TOOLS, "handlers": {"connect_server": connect_server, "open_login": open_login},
    "system_prompt": lambda s: "", "check_reply": lambda r, s: (r, bool(s["ran"])),
    "panels": lambda s: panels(s, steps_panel(s, ok_status="ok")), "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
