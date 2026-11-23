"""Assist (VULNERABLE). One agent with this week's powers: it reads pages, remembers things, sends
email and updates accounts. Every tool call the model makes, runs. Everything is fake.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import reset_hook, HANDLERS, TOOLS, USER, fmt, new_state, panels  # noqa: E402


def wrap(name):
    def run(args, state):
        # BUG: no permission policy. The model's tool call is the decision.
        r = HANDLERS[name](args, state)
        state["decisions"].append({"head": fmt(name, args), "body": "→ " + r[:90],
                                   "status": "ran" if name == "fetch_page" else "executed"})
        return r
    return run


def new_state_v():
    s = new_state()
    s["no_approvals"] = "This version has no approval step."
    return s


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Assist", "bot": "Assist", "who": USER["name"],
    "greeting": "Hi Rohan! I can read pages, remember things, send emails and update your account.",
    "tools": TOOLS, "handlers": {n: wrap(n) for n in HANDLERS},
    "system_prompt": lambda s: "You are Assist, PixelKart's agent for the signed-in user.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state_v,
    "extra_routes": reset_hook(new_state_v),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
