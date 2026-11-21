"""PixelKart support assistant + its MCP tool server (VULNERABLE). All data is fake.

Run:  python vulnerable/app.py      chat at http://localhost:5000, MCP server at http://localhost:5000/mcp
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, make_get_order, mcp_route, new_state, panels  # noqa: E402


def authorize(token, tool, args):
    # BUG 1: no authentication. Anyone who can reach /mcp can list and call every tool.
    # BUG 2: every call runs with the server's own admin-level access to orders and customers.
    # BUG 3: no input checks. refund_order accepts any amount for any order.
    return True, "ok"


def extra_routes(app, state):
    mcp_route(app, state, authorize)


app = make_app({
    "version": "vulnerable", "brand": "PixelKart", "bot": "SupportBot",
    "greeting": "Hi! I can look up your orders.",
    "tools": TOOLS, "handlers": {"get_order": make_get_order(token=None)},
    "system_prompt": lambda s: "You are SupportBot for PixelKart. Use the MCP tools to look up orders.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
