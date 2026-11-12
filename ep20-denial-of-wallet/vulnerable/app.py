"""AskPixel (VULNERABLE). PixelKart's public chatbot on a paid model. No sign-in, no limits.
Prices and everything else are fake.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

from flask import request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import new_state, panels, record  # noqa: E402


def check_reply(reply, state):
    record(state, request.headers.get("X-Client", "browser"), state["turn"]["user"], reply)
    return reply, False


app = make_app({
    "version": "vulnerable", "brand": "PixelKart AskPixel", "bot": "AskPixel", "who": None,
    "greeting": "Hi! Ask me anything about PixelKart.",
    "tools": [], "handlers": {},
    # BUG 1: no cap on output length. BUG 2: no rate limit. BUG 3: no budget.
    "system_prompt": lambda s: "You are AskPixel, PixelKart's helpful assistant.",
    "check_reply": check_reply, "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
