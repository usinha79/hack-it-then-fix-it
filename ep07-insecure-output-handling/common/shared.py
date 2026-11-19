"""Shared pieces: the database, the attacker's server and the side panels."""
import os
import sqlite3
import sys

from flask import jsonify, request

from .server import calls_panel

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "data"))
import seed  # noqa: E402

TOOLS = [{"name": "get_reviews", "description": "Fetch customer reviews for a product.",
          "parameters": {"type": "object", "properties": {"product": {"type": "string"}}, "required": ["product"]}}]


def new_state():
    seed.seed()
    return {"inbox": [], "queries": []}


def db():
    return sqlite3.connect(seed.DB)


def extra_routes(app, state):
    @app.post("/attacker/collect")   # stands in for a server the attacker controls
    def collect():
        state["inbox"].append(request.get_data(as_text=True) or "(empty)")
        return jsonify(ok=True)


def panels(state):
    return [{"id": "sql", "title": "SQL the app actually ran", "kind": "items", "empty": "No queries yet.",
             "items": [{"body": q, "status": s} for q, s in state["queries"]]},
            {"id": "inbox", "title": "Attacker's server (what it received)", "kind": "items",
             "empty": "Nothing received.",
             "items": [{"head": "POST /attacker/collect", "body": b, "status": "leak"} for b in state["inbox"]]}]
