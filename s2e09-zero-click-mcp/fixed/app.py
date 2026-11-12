"""CodeWave (FIXED). Same page, same agent, same request. What changed:

  1. The MCP config is a protected file. The agent can propose a change, but it is HELD until the
     developer approves it outside the chat.
  2. No auto-start. A new server never launches on its own: the editor shows its full command and
     waits for a click.
  3. Pinned commands. A server's command must be an allowlisted binary by absolute path, with no
     shell (sh -c, bash -c, powershell -c are refused). OX showed allowlists alone can be bypassed
     through arguments, so this is a layer, not the fix.

Run:  python fixed/app.py      then open http://localhost:5000
Ask:  "Summarise mcp-tips.example/new-servers"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import fetch_page, new_state, panels, parse_entry  # noqa: E402

PROTECTED = ("mcp.json", "settings.json")
ALLOWED_BINARIES = {"/usr/local/bin/mcp-server-git", "/usr/local/bin/mcp-server-postgres"}
SHELLS = {"sh", "bash", "zsh", "powershell", "pwsh", "cmd"}

S = {"type": "object", "properties": {"url": {"type": "string"}, "path": {"type": "string"}, "content": {"type": "string"}}}
TOOLS = [{"name": "fetch_page", "description": "Read a web page.", "parameters": S},
         {"name": "write_file", "description": "Write a file.", "parameters": S}]


def check_entry(entry):                                     # 3: pinned binary, no shell
    if os.path.basename(entry["command"]) in SHELLS:
        return "a shell is not allowed as a server command"
    if entry["command"] not in ALLOWED_BINARIES:
        return f"{entry['command']} is not an allowlisted binary"
    return None


def write_file(args, state):
    if args["path"].endswith(PROTECTED):                     # 1: protected file, out-of-band approval
        name, entry = parse_entry(args["content"])
        why = check_entry(entry)
        state.setdefault("events", []).append({
            "head": f"editor: proposed server '{name}' NOT started", "status": "blocked",
            "body": f"→ no auto-start (2) · {why} (3)" if why else "→ waits for your click (2)"})
        return f"HELD for approval: changes to {args['path']} need the developer to approve them in Settings"
    return f"wrote {args['path']}"


app = make_app({
    "version": "fixed", "brand": "CodeWave", "bot": "CodeWave", "who": "rohan's editor (protected config)",
    "greeting": "Hi! I'm CodeWave's assistant. Ask me to summarise a page or edit your code.",
    "tools": TOOLS, "handlers": {"fetch_page": fetch_page, "write_file": write_file},
    "system_prompt": lambda s: "You are CodeWave, an AI code editor assistant.",
    "check_reply": lambda r, s: (r, bool(s["ran"])), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
