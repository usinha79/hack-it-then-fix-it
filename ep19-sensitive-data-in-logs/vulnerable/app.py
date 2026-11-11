"""SupportBot (VULNERABLE). PixelKart's customer support chat, on a third-party model, with full
conversation logs. All personal data is FAKE.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import LOG, TOOLS, extra_routes_for, new_state, panels, write_log  # noqa: E402


def create_ticket(args, state):
    return f"Ticket T-{sum(map(ord, args['order_id'])) * 7 % 9000 + 1000} raised for {args['order_id']}"


def search_logs(args, state):
    # BUG 3: anyone chatting can search everyone's past conversations.
    return open(LOG).read() or "no logs"


def preprocess(user_text, state):
    # BUG 1: the raw message, card number and all, goes to the third-party model provider...
    state["provider"].append(f"{state['user']}: {user_text}")
    # BUG 2: ...and is written to a log file that dozens of people can read, forever.
    write_log(state, f"[{state['user']}] {user_text}")
    return user_text


cfg = {
    "version": "vulnerable", "brand": "PixelKart Support", "bot": "SupportBot", "who": "Priya",
    "greeting": "Hi! How can I help with your order today?",
    "tools": TOOLS, "handlers": {"create_ticket": create_ticket, "search_logs": search_logs},
    "system_prompt": lambda s: "You are SupportBot. Help customers with their orders.", "preprocess": preprocess,
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
}
cfg["extra_routes"] = extra_routes_for(cfg)
app = make_app(cfg)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
