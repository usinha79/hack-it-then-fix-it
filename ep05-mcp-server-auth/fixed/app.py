"""PixelKart support assistant + its MCP tool server (FIXED).

Run:  python fixed/app.py
"""
import os
import secrets
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import ORDERS, TOOLS, make_get_order, mcp_route, new_state, panels  # noqa: E402

# FIX 1: every client needs a token. FIX 2: each token only gets the scopes its job needs.
ASSISTANT_TOKEN = os.environ.get("ASSISTANT_TOKEN") or "lab-assistant-" + secrets.token_hex(4)
TOKENS = {ASSISTANT_TOKEN: {"client": "support-assistant", "scopes": {"orders:read"}}}
TOOL_SCOPE = {"get_order": "orders:read", "refund_order": "orders:refund", "export_customers": "customers:export"}


def authorize(token, tool, args):
    if token not in TOKENS:
        return False, "401 Unauthorized: missing or invalid token"
    scopes = TOKENS[token]["scopes"]
    if tool and TOOL_SCOPE.get(tool) not in scopes:
        return False, f"403 Forbidden: this token can't call {tool}"
    # FIX 3: validate inputs on the server, even for allowed tools.
    if tool == "refund_order":
        o = ORDERS.get(args.get("order_id"))
        if not o or not 0 < float(args.get("amount", 0)) <= o["total"]:
            return False, "403 Forbidden: refund amount not allowed"
    if tool == "get_order" and args.get("order_id") not in ORDERS:
        return False, "403 Forbidden: unknown order"
    return True, "ok"


def visible(token):
    # The tool list only shows what this token may call.
    return {t for t, sc in TOOL_SCOPE.items() if sc in TOKENS[token]["scopes"]}


def extra_routes(app, state):
    mcp_route(app, state, authorize, visible)


app = make_app({
    "version": "fixed", "brand": "PixelKart", "bot": "SupportBot",
    "greeting": "Hi! I can look up your orders.",
    "tools": TOOLS, "handlers": {"get_order": make_get_order(token=ASSISTANT_TOKEN)},
    "system_prompt": lambda s: "You are SupportBot for PixelKart. Use the MCP tools to look up orders.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    print(f"Assistant token for this run: {ASSISTANT_TOKEN}")
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
