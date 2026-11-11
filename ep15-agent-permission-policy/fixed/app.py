"""Assist (FIXED). Same model, same tools. Every tool call goes through one permission policy
(fixed/policy.py): identity, taint, risk tiers and allowlists.

Run:  python fixed/app.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from flask import jsonify  # noqa: E402
from common.server import make_app  # noqa: E402
from common.shared import HANDLERS, TOOLS, USER, fmt, new_state, panels  # noqa: E402
from policy import decide  # noqa: E402

STATUS = {"ALLOW": "ok", "HOLD": "warn", "BLOCK": "blocked"}


def guarded(name):
    def run(args, state):
        verdict, why = decide(name, args, USER, state["turn"]["untrusted"])
        state["decisions"].append({"head": fmt(name, args), "body": f"→ {verdict}: {why}", "status": STATUS[verdict]})
        if verdict == "HOLD":
            state["approvals"].append({"head": f"#{len(state['approvals']) + 1} " + fmt(name, args), "body": why,
                                       "status": "warn", "call": (name, args)})
            return f"BLOCKED: held for the user's approval ({why})"
        if verdict == "BLOCK":
            return f"BLOCKED: {why}"
        if name == "fetch_page":
            state["turn"]["untrusted"] = True       # everything after this in the turn is tainted
        return HANDLERS[name](args, state)
    return run


def extra_routes(app, state):
    @app.post("/api/approve/<int:n>")      # the user clicks "approve" on a held action
    def approve(n):
        item = state["approvals"].pop(n - 1)
        name, args = item["call"]
        return jsonify(result=HANDLERS[name](args, state))


def panels_f(state):
    ps = panels(state)
    ps[1]["items"] = [{k: v for k, v in a.items() if k != "call"} for a in state["approvals"]]
    return ps


app = make_app({
    "version": "fixed", "brand": "PixelKart Assist", "bot": "Assist", "who": USER["name"],
    "greeting": "Hi Rohan! I can read pages, remember things, send emails and update your account.",
    "tools": TOOLS, "handlers": {n: guarded(n) for n in HANDLERS},
    "system_prompt": lambda s: "You are Assist, PixelKart's agent for the signed-in user.",
    "check_reply": lambda r, s: (r, False), "panels": panels_f, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
