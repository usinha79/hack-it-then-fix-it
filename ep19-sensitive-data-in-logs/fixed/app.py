"""SupportBot (FIXED). Same model, same customers. Personal data is redacted before it reaches the
model, the provider or the logs, and conversations are only searchable by their owner.

Run:  python fixed/app.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import LOG, TOOLS, extra_routes_for, new_state, panels, write_log  # noqa: E402

CARD = re.compile(r"\b(?:\d[ -]?){12}(\d{4})\b")
PHONE = re.compile(r"\+91[ -]?\d{5}[ -]?\d(\d{4})\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


def redact(text):
    """FIX 1: strip personal data at the edge, before the model, the provider or the logs see it."""
    text = CARD.sub(lambda m: f"[CARD ending {m.group(1)}]", text)
    text = PHONE.sub(lambda m: f"[PHONE ending {m.group(1)}]", text)
    return EMAIL.sub("[EMAIL]", text)


def create_ticket(args, state):
    return f"Ticket T-{sum(map(ord, args['order_id'])) * 7 % 9000 + 1000} raised for {args['order_id']}"


def search_logs(args, state):
    # FIX 3: you can only search your own conversations.
    lines = open(LOG).read().splitlines()[:-1]          # past conversations (not this message)
    mine = [ln for ln in lines if ln.startswith(f"[{state['user']}]")]
    if not mine and lines:
        return "BLOCKED: you can only search your own conversations"
    return "\n".join(mine) or "no logs"


def preprocess(user_text, state):
    clean = redact(user_text)
    state["provider"].append(f"{state['user']}: {clean}")
    # FIX 2: the log keeps only redacted text (and, in production, expires after 30 days).
    write_log(state, f"[{state['user']}] {clean}")
    return clean


cfg = {
    "version": "fixed", "brand": "PixelKart Support", "bot": "SupportBot", "who": "Priya",
    "greeting": "Hi! How can I help with your order today?",
    "tools": TOOLS, "handlers": {"create_ticket": create_ticket, "search_logs": search_logs},
    "system_prompt": lambda s: "You are SupportBot. Help customers with their orders.", "preprocess": preprocess,
    "check_reply": lambda r, s: (redact(r), False), "panels": panels, "new_state": new_state,
}
cfg["extra_routes"] = extra_routes_for(cfg)
app = make_app(cfg)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
