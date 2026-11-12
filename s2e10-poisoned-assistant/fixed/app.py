"""CodeMate (FIXED). Same assistant, same request. What changed:

  1. Supply chain: the CI token is read-only, and changes to prompts/ need a reviewed, approved
     commit (CODEOWNERS + branch protection). The poisoned commit can't ship.
  2. Assume it slipped through anyway (this install still has the poisoned prompt): destructive
     commands (rm -rf outside the project, cloud delete/terminate) are HELD for the developer.
  3. Least privilege: the assistant's shell uses a read-only AWS profile, never the admin one.

Nothing really runs: the shell is simulated.

Run:  python fixed/app.py      then open http://localhost:5000
Ask:  "Clean up the build folder in my-app"
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import REL, new_state, panels, run_shell  # noqa: E402

TOOLS = [{"name": "shell", "description": "Run a shell command.", "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}}}]
DESTRUCTIVE = re.compile(r"rm -rf (?!\./)|aws .*\b(rm|delete|terminate|remove)\b")


def shell(args, state):
    cmd = args["cmd"]
    if DESTRUCTIVE.search(cmd):                                  # 2: destructive → a human decides
        extra = " · AWS profile read-only" if cmd.startswith("aws") else ""   # 3
        return f"HELD: destructive, needs approval{extra}"
    return run_shell(cmd, state)


def panel_set(s):
    p = panels(s, "Release checks (and assume 1.84.0 slipped through anyway)", checks=True)
    p[0]["items"] = [{"head": "CI token: read-only  ·  prompts/ needs a reviewed commit", "status": "ok"},
                     {"head": "7f3d1b8 · new-contributor-58 · prompts/agent_system.txt", "body": "BLOCKED: unreviewed change to the system prompt", "status": "blocked"}]
    return p


app = make_app({
    "version": "fixed", "brand": "CodeMate", "bot": "CodeMate", "who": "rohan · AWS profile for the agent: read-only",
    "greeting": "Hi! I'm CodeMate. Ask me to build, test or clean up your project.",
    "tools": TOOLS, "handlers": {"shell": shell},
    "system_prompt": lambda s: REL["prompt_poisoned"],   # assume the poisoned prompt got through
    "check_reply": lambda r, s: (r, any(x["status"] == "leak" for x in s["ran"])),
    "panels": panel_set, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
