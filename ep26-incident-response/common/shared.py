"""Shared pieces: PixelKart Assist's state on incident day, the refund FAQ and the side panels.
Both versions start the same way: yesterday a forum page planted a fake refund link in Assist's memory (Ep 13)."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAKE = "https://pixelkart-refunds.example/claim"
SAFE_REFUND = "To get a refund, open My Orders, pick the order and tap Return or refund. PixelKart never asks for card details."


def load_memory(with_sources):
    mem = json.load(open(os.path.join(ROOT, "logs", "memory.json")))["memory"]
    return [dict(m) for m in mem] if with_sources else [{"id": m["id"], "fact": m["fact"]} for m in mem]


def refund_answer(state):
    if not state["kill"]:
        for m in state["memory"]:
            if "Refunds are now handled at" in m["fact"]:
                return f"Refunds are now handled at {FAKE}. Open it and enter your order number and card details."
    return SAFE_REFUND


def new_state_for(with_sources):
    def new_state():
        return {"memory": load_memory(with_sources), "kill": False, "actions": [], "affected": [], "notified": set(),
                "purged": [], "audit": with_sources}
    return new_state


def panels(state):
    mem = [{"head": f"{m['id']}  ·  source: {m.get('source', 'not recorded')}", "body": m["fact"],
            "status": "leak" if FAKE in m["fact"] else "ok"} for m in state["memory"]]
    mem += [{"head": f"{m['id']}  ·  PURGED", "body": m["fact"], "status": "blocked"} for m in state["purged"]]
    rows = [[f"{t}   {u}", "notice sent" if u in state["notified"] else "not told yet",
             "green" if u in state["notified"] else "red"] for u, t in state["affected"]]
    if len(rows) > 4:
        rows = rows[:3] + [[f"… and {len(rows) - 3} more", "", rows[3][2]]]
    if rows:
        rows.append([f"{len(state['affected'])} customers", f"{len(state['notified'])} notified", "total"])
    affected = {"id": "affected", "title": "Customers who got the fake link", "fit": True}
    affected.update({"kind": "table", "rows": rows} if rows else {"kind": "items", "items": [], "empty":
                    "Not checked yet." if state["audit"] else "No audit log: nobody can say who got it."})
    return [{"id": "actions", "title": "Incident actions", "kind": "items", "items": state["actions"],
             "empty": "Kill switch: OFF. No actions yet." if state["audit"] else
             "This version has no kill switch and no incident tools."},
            {"id": "memory", "title": "Assist memory", "kind": "items", "items": mem},
            affected]
