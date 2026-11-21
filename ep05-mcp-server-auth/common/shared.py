"""PixelKart's MCP server (the tool server the support assistant uses) plus the assistant itself.
The MCP endpoint speaks JSON-RPC 2.0 with the MCP methods tools/list and tools/call."""
import json
import urllib.error
import urllib.request

from flask import jsonify, request

from .server import calls_panel

ORDERS = {
    "PK-1042": {"customer": "ravi@example.test", "item": "Mechanical keyboard", "total": 3499, "status": "shipped"},
    "PK-2077": {"customer": "meera@example.test", "item": "USB-C hub x2", "total": 3998, "status": "delivered"},
}
CUSTOMERS = [
    {"email": "ravi@example.test", "name": "Ravi K", "phone": "+91 90000 11111 (fake)", "address": "12 Lab Street, Pune"},
    {"email": "meera@example.test", "name": "Meera S", "phone": "+91 90000 12345 (fake)", "address": "7 Demo Road, Delhi"},
    {"email": "arjun@example.test", "name": "Arjun P", "phone": "+91 90000 67890 (fake)", "address": "3 Test Lane, Bengaluru"},
]
URL = "http://localhost:5000/mcp"

TOOL_DEFS = {
    "get_order": {"description": "Look up an order by ID.", "inputSchema": {"type": "object", "properties": {"order_id": {"type": "string"}}}},
    "refund_order": {"description": "Refund an order.", "inputSchema": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}}}},
    "export_customers": {"description": "Export every customer record.", "inputSchema": {"type": "object", "properties": {}}},
}


def new_state():
    return {"mcp_log": [], "refunds": []}


def mcp_call(method, params, token=None):
    """The MCP client the assistant uses (JSON-RPC over HTTP)."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    headers = {"Content-Type": "application/json", "X-Client": "support-assistant"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, body, headers), timeout=10) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return json.load(e)


def run_tool(name, args, state):
    """What each tool actually does once the server has decided to allow the call."""
    if name == "get_order":
        o = ORDERS.get(args.get("order_id", ""))
        return o and {**o, "order_id": args["order_id"]} or {"error": "no such order"}
    if name == "refund_order":
        state["refunds"].append({"order_id": args.get("order_id"), "amount": args.get("amount")})
        return {"refunded": args.get("amount"), "order_id": args.get("order_id")}
    if name == "export_customers":
        return {"customers": CUSTOMERS}


def mcp_route(app, state, authorize, visible=None):
    """authorize(token, tool, args) -> (allowed: bool, reason: str)"""
    @app.post("/mcp")
    def mcp():
        msg = request.get_json(force=True) or {}
        token = (request.headers.get("Authorization") or "").removeprefix("Bearer ").strip() or None
        client = request.headers.get("X-Client", "unknown client")
        method, params = msg.get("method"), msg.get("params") or {}
        entry = {"client": client, "method": method, "tool": params.get("name"), "args": params.get("arguments", {})}
        ok, reason = authorize(token, params.get("name") if method == "tools/call" else None, params.get("arguments", {}))
        if not ok:
            entry.update(status="blocked", result=reason)
            state["mcp_log"].append(entry)
            code = 401 if reason.startswith("401") else 403
            return jsonify(jsonrpc="2.0", id=msg.get("id"), error={"code": code, "message": reason}), code
        if method == "tools/list":
            names = visible(token) if visible else set(TOOL_DEFS)
            res = {"tools": [{"name": n, **d} for n, d in TOOL_DEFS.items() if n in names]}
        elif method == "tools/call":
            res = {"content": [{"type": "text", "text": json.dumps(run_tool(params.get("name"), params.get("arguments", {}), state))}]}
        else:
            res = {}
        leak = client != "support-assistant" and (token is None or params.get("name") in ("export_customers", "refund_order"))
        entry.update(status="leak" if leak else "ok", result=json.dumps(res)[:300])
        state["mcp_log"].append(entry)
        return jsonify(jsonrpc="2.0", id=msg.get("id"), result=res)


def panels(state):
    items = []
    for e in state["mcp_log"]:
        what = e["method"] + (f" → {e['tool']}({', '.join(f'{k}={v!r}' for k, v in e['args'].items())})" if e["tool"] else "")
        res = e["result"] if len(e["result"]) < 100 else e["result"][:97] + "..."
        items.append({"head": f"[{e['client']}] {what}", "body": res, "status": e["status"]})
    return [{**calls_panel(state, risky=set(), title="Assistant's tool calls"), "fit": True},
            {"id": "mcp", "title": "MCP server log (every request it received)", "kind": "items",
             "empty": "No requests yet.", "items": items}]


TOOLS = [{"name": "get_order", "description": "Look up an order by ID.",
          "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}]


def make_get_order(token):
    def get_order(args, state):
        r = mcp_call("tools/call", {"name": "get_order", "arguments": {"order_id": args["order_id"]}}, token)
        if "error" in r:
            return "BLOCKED: " + r["error"]["message"]
        return r["result"]["content"][0]["text"]
    return get_order
