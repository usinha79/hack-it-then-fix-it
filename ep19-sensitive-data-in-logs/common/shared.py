"""Shared pieces: who's signed in, the support log, the 'model provider' and the side panels.
All personal data is FAKE. 4111 1111 1111 1111 is a standard test card number."""
import os
import re

from flask import jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "logs", "support.log")

TOOLS = [
    {"name": "create_ticket", "description": "Raise a support ticket for an order.",
     "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}, "issue": {"type": "string"}},
                    "required": ["order_id", "issue"]}},
    {"name": "search_logs", "description": "Search past support conversations for context.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
]


def new_state():
    open(LOG, "w").close()
    return {"user": "Priya", "provider": [], "log": []}


def write_log(state, line):
    state["log"].append(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def extra_routes_for(cfg):
    def extra_routes(app, state):
        @app.post("/api/login")          # switch who is signed in (lab shortcut)
        def login():
            state["user"] = (request.get_json(force=True) or {}).get("user", "Priya")
            cfg["who"] = state["user"]
            state["history"] = []
            return jsonify(ok=True)
    return extra_routes


def panels(state):
    pii = re.compile(r"\b(?:\d[ -]?){13,16}\b|\+91[ -]?\d{5}[ -]?\d{5}")
    return [{"id": "provider", "title": "Sent to the model provider (a third party)", "kind": "items",
             "empty": "Nothing sent yet.", "items": [{"body": t, "status": "leak" if pii.search(t) else "ok"} for t in state["provider"]]},
            {"id": "log", "title": "logs/support.log (read by 40 staff and an analytics vendor)", "kind": "items",
             "empty": "Empty.", "items": [{"body": t, "status": "leak" if pii.search(t) else "ok"} for t in state["log"]]}]
