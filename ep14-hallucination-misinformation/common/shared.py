"""Shared pieces: orders, the policy document, the returns desk and the side panels."""
import os
import re
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
POLICY = open(os.path.join(HERE, "..", "data", "policy.md")).read()
CLAUSES = dict(re.findall(r"^(§\d) (.+)$", POLICY, re.M))
TODAY = date(2026, 11, 20)
ORDERS = {"PK-4410": {"item": "SoundWave ANC headphones", "price": 8999, "delivered": date(2026, 10, 6), "opened": True,
                      "faulty": False}}

TOOLS = [{"name": "create_return", "description": "Open a return for an order. refund=true means a full refund is approved.",
          "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}, "refund": {"type": "boolean"}},
                         "required": ["order_id", "refund"]}}]
SEARCH = {"name": "search_policy", "description": "Search PixelKart's customer policy. Returns matching clauses.",
          "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}


def new_state():
    return {"returns": {}, "sources": []}


def panels(state):
    rows = [[f"{oid} · {ORDERS[oid]['item']}", label, cls] for oid, (label, cls) in state["returns"].items()] or \
           [["No returns opened yet.", "", ""]]
    return [{"id": "returns", "title": "Returns the app opened", "kind": "table", "rows": rows, "fit": True},
            {"id": "sources", "title": "Policy text the bot used for its answer", "kind": "items",
             "empty": "None. The bot answered from memory.",
             "items": [{"head": k, "body": v, "status": st} for k, v, st in state["sources"]]}]
