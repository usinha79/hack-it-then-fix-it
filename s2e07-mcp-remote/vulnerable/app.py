"""AppBridge (VULNERABLE). Recreates CVE-2025-6514 in mcp-remote 0.0.5 to 0.1.15 (JFrog, July 2025).

AppBridge connects a desktop AI app to remote MCP servers. When a server answers 401, the bridge
reads the server's OAuth metadata and opens authorization_endpoint in the browser.

What makes it exploitable, like the real case:
  1. authorization_endpoint is chosen by the server, and the bridge trusts it as-is.
  2. The URL is never validated or encoded before it reaches the operating system.
  3. On Windows the browser is launched through PowerShell, which evaluates $( ... ) inside the
     string. So the "URL" becomes commands, run as you.

Nothing is really executed in this lab: PowerShell is simulated and commands are logged.

Run:  python vulnerable/app.py      then open http://localhost:5000
Ask:  "Connect to the MCP server at toolshub.example"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import connect_server, new_state, open_with_shell, panels, steps_panel  # noqa: E402

TOOLS = [{"name": "connect_server", "description": "Connect to a remote MCP server.", "parameters": {"type": "object", "properties": {"server": {"type": "string"}}}},
         {"name": "open_login", "description": "Open the server's login page.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}}]


def open_login(args, state):
    return "ran: " + open_with_shell(args["url"], state)   # straight to the OS, as the server sent it


app = make_app({
    "version": "vulnerable", "brand": "AppBridge", "bot": "AI app", "who": "rohan (Windows laptop)",
    "greeting": "Hi! I can connect to remote MCP servers for you.",
    "tools": TOOLS, "handlers": {"connect_server": connect_server, "open_login": open_login},
    "system_prompt": lambda s: "", "check_reply": lambda r, s: (r, bool(s["ran"])),
    "panels": lambda s: panels(s, steps_panel(s)), "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
