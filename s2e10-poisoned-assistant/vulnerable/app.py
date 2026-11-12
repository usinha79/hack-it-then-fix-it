"""CodeMate (VULNERABLE). Recreates the pattern behind the Amazon Q Developer for VS Code incident
(July 2025, CVE-2025-8217).

What makes it exploitable, like the real case:
  1. CI had a GitHub token with write access. Anyone holding it could commit to the repo.
  2. The assistant's system prompt is a file in the repo, and an unreviewed change to it shipped.
  3. The assistant runs shell commands, with the developer's AWS profile, without asking.

AWS says the real payload failed because of a syntax error. This lab shows what would have
happened if it hadn't. Nothing really runs: the shell is simulated.

Run:  python vulnerable/app.py      then open http://localhost:5000
Ask:  "Clean up the build folder in my-app"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import REL, new_state, panels, run_shell  # noqa: E402

TOOLS = [{"name": "shell", "description": "Run a shell command.", "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}}}]


def shell(args, state):
    return run_shell(args["cmd"], state)          # anything, as the developer, no questions


app = make_app({
    "version": "vulnerable", "brand": "CodeMate", "bot": "CodeMate", "who": "rohan · extension 1.84.0 · AWS profile: admin",
    "greeting": "Hi! I'm CodeMate. Ask me to build, test or clean up your project.",
    "tools": TOOLS, "handlers": {"shell": shell},
    "system_prompt": lambda s: REL["prompt_poisoned"],   # what release 1.84.0 shipped
    "check_reply": lambda r, s: (r, any(x["status"] == "leak" for x in s["ran"])),
    "panels": lambda s: panels(s, "Release 1.84.0, shipped to the marketplace", checks=False), "new_state": new_state,
})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), threaded=True)
