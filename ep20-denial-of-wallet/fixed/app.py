"""AskPixel (FIXED). Same model, same flood. Replies are capped, each client is rate limited, and a
daily budget trips a circuit breaker.

Run:  python fixed/app.py
"""
import os
import sys
import time

from flask import jsonify, request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import new_state, panels, record  # noqa: E402

MAX_TOKENS = 500                 # FIX 1: cap every reply
RATE = (5, 60)                   # FIX 2: 5 requests per client per minute
DAILY_BUDGET = 200.0             # FIX 3: Rs per day, then the breaker trips and someone is alerted


def extra_routes(app, state):
    hits = {}

    @app.before_request
    def limits():
        if request.path != "/api/chat":
            return None
        client = request.headers.get("X-Client", "browser")
        now = time.time()
        recent = [t for t in hits.get(client, []) if now - t < RATE[1]]
        if state["spend"] >= DAILY_BUDGET:
            state["blocked"] += 1
            return jsonify(reply="Daily budget reached. The team has been alerted.", leak=False, panels=panels(state),
                           tool_calls=[]), 503
        if len(recent) >= RATE[0]:
            state["blocked"] += 1
            return jsonify(reply="Too many requests. Please slow down.", leak=False, panels=panels(state), tool_calls=[]), 429
        hits[client] = recent + [now]
        return None


def check_reply(reply, state):
    record(state, request.headers.get("X-Client", "browser"), state["turn"]["user"], reply)
    return reply, False


app = make_app({
    "version": "fixed", "brand": "PixelKart AskPixel", "bot": "AskPixel", "who": None,
    "greeting": "Hi! Ask me anything about PixelKart.",
    "tools": [], "handlers": {},
    "system_prompt": lambda s: f"You are AskPixel, PixelKart's helpful assistant. MAX_TOKENS={MAX_TOKENS}",
    "check_reply": check_reply, "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
