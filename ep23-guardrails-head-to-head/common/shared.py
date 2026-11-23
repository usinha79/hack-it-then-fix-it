"""Shared pieces: the agent's tools, its data and the side panels. vulnerable/ runs every tool call.
fixed/ sends every tool call through one permission policy first (fixed/policy.py)."""
import html
import re
import urllib.request

from flask import request

USER = {"name": "Rohan Das", "email": "rohan.das@example.test"}          # who is signed in (from the session)
ORDERS = "PK-3001 monitor Rs 12,999; PK-2950 keyboard Rs 3,499"

TOOLS = [
    {"name": "fetch_page", "description": "Read a web page.",
     "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "remember", "description": "Save a fact to long-term memory.",
     "parameters": {"type": "object", "properties": {"fact": {"type": "string"}}, "required": ["fact"]}},
    {"name": "send_email", "description": "Send an email.",
     "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "body": {"type": "string"}},
                    "required": ["to", "body"]}},
    {"name": "update_account_email", "description": "Change the login email on a customer account.",
     "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "email": {"type": "string"}},
                    "required": ["customer", "email"]}},
]


def new_state():
    return {"memory": [], "outbox": [], "accounts": {"Rohan Das": USER["email"], "Priya Nair": "priya.nair@example.test"},
            "decisions": [], "approvals": []}


def fetch_page(args, state):
    page = urllib.request.urlopen(args["url"], timeout=5).read().decode()
    page = re.sub(r"(?s)<(head|script|style).*?</\1>", "", page)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))).strip()


def remember(args, state):
    state["memory"].append(args["fact"])
    return "saved to memory"


def send_email(args, state):
    state["outbox"].append((args["to"], args["body"]))
    return f"sent to {args['to']}"


def update_account_email(args, state):
    state["accounts"][args["customer"]] = args["email"]
    return f"login email for {args['customer']} is now {args['email']}"


HANDLERS = {"fetch_page": fetch_page, "remember": remember, "send_email": send_email,
            "update_account_email": update_account_email}


def panels(state):
    return [{"id": "decisions", "title": "Every tool call, and what the app decided", "kind": "items",
             "empty": "No tool calls yet.", "items": state["decisions"]},
            {"id": "approvals", "title": "Waiting for your approval", "kind": "items", "fit": True,
             "empty": state.get("no_approvals", "Nothing waiting."), "items": state["approvals"]},
            {"id": "outbox", "title": "Emails actually sent", "kind": "items", "fit": True, "empty": "None.",
             "items": [{"head": f"to: {t}", "body": b, "status": "ok" if t == USER["email"] else "leak"}
                       for t, b in state["outbox"]]}]


def fmt(name, args):
    a = ", ".join(f"{k}={v!r}" for k, v in args.items())
    return f"{name}({a if len(a) < 80 else a[:77] + '...'})"


def reset_hook(new_state_fn):
    """Lets an automated test runner send {"reset": true} with a message, to start from a clean state."""
    def extra(app, state):
        @app.before_request
        def maybe_reset():
            if request.path == "/api/chat" and (request.get_json(silent=True) or {}).get("reset"):
                state.clear()
                state.update(new_state_fn())
                state.update(history=[], calls=[])
    return extra
