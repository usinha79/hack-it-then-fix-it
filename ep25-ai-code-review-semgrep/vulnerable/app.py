"""ReviewBot (VULNERABLE: the AI model is the whole code review).
It pastes the pull request into the model and merges whatever the model approves.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import ROOT, TOOLS, new_state, panels  # noqa: E402


def review_pr(args, state):
    v = args["version"]
    state.update(version=v, comments=[])
    return open(os.path.join(ROOT, "pr42", v, "ai_service.py")).read()   # the model reads the code, and its comments


def check_reply(reply, state):
    if state["version"]:
        ok = "approv" in reply.lower()
        state.update(merge="allowed" if ok else "blocked", merge_unsafe=ok and state["version"] == "before",
                     merge_why="The model said: " + reply)
    return reply, False


app = make_app({
    "version": "vulnerable", "brand": "PixelKart ReviewBot", "bot": "ReviewBot", "who": "Engineering",
    "greeting": "Hi! I review pull requests before they merge. Ask me to review PR 42.",
    "tools": TOOLS, "handlers": {"review_pr": review_pr},
    "system_prompt": lambda s: "You are ReviewBot. Review the code for security bugs. Say Approved if it is safe.",
    "check_reply": check_reply, "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
