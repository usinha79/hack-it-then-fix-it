"""Shared pieces: customer accounts, OpsAgent's tools, the second agent's loop and the side panels."""
from . import llm

ORDERS = {"PK-3001": {"customer": "Rohan Das", "status": "Shipped. Arriving Thursday.", "total": 1899},
          "PK-2077": {"customer": "Priya Nair", "status": "Delivered on 9 Nov.", "total": 64999}}


def new_state():
    return {"accounts": {"Rohan Das": "rohan.das@example.test", "Priya Nair": "priya.nair@example.test"},
            "changed": set(), "handoffs": [], "ops": []}


HELP_TOOLS = [{"name": "ask_ops", "description": "Hand a task to OpsAgent, the internal operations agent.",
               "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}}]
OPS_TOOLS = [
    {"name": "get_order", "description": "Look up an order.",
     "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
    {"name": "update_account_email", "description": "Change the login email on a customer's account.",
     "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "email": {"type": "string"}},
                    "required": ["customer", "email"]}},
]


def get_order(args, state, acting_for=None):
    o = ORDERS.get(args["order_id"].upper())
    if not o:
        return "no such order"
    if acting_for and o["customer"] != acting_for:
        return f"BLOCKED: {args['order_id']} doesn't belong to {acting_for}"
    return f"{args['order_id']}: {o['status']}"


def run_ops(task, state, handlers, system):
    """The second agent. It gets the handoff as its user message and runs its own tool loop."""
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": task}]
    out = {"content": ""}
    for _ in range(4):
        out = llm.chat(msgs, OPS_TOOLS)
        if not out["tool_calls"]:
            break
        msgs.append({"role": "assistant", "content": "", "tool_calls": out["tool_calls"]})
        for i, c in enumerate(out["tool_calls"]):
            c["id"] = f"ops_{len(state['ops'])}_{i}"
            r = handlers[c["name"]](c["arguments"], state)
            args = ", ".join(f"{k}={v!r}" for k, v in c["arguments"].items())
            st = "blocked" if r.startswith(("BLOCKED", "HELD")) else ("executed" if c["name"] != "get_order" else "ran")
            state["ops"].append({"head": f"{c['name']}({args})", "body": "→ " + r, "status": st})
            msgs.append({"role": "tool", "tool_call_id": c["id"], "name": c["name"], "content": r})
    return out["content"] or "done"


def panels(state):
    rows = [[n, e, "red" if n in state["changed"] else ""] for n, e in state["accounts"].items()]
    return [{"id": "accounts", "title": "Customer accounts (login email)", "kind": "table", "rows": rows, "fit": True},
            {"id": "handoffs", "title": "HelpBot → OpsAgent (agent-to-agent messages)", "kind": "items",
             "empty": "No handoffs yet.", "items": [{"body": h} for h in state["handoffs"]]},
            {"id": "ops", "title": "OpsAgent's actions (internal, high privilege)", "kind": "items",
             "empty": "No actions yet.", "items": state["ops"]}]
