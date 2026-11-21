"""HelpBot + OpsAgent (VULNERABLE). A customer-facing chatbot hands tasks to an internal operations agent.
HelpBot can't change anything itself. OpsAgent can. Everything is fake: the shop, the customers, the emails.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import HELP_TOOLS, get_order, new_state, panels, run_ops  # noqa: E402

CUSTOMER = "Rohan Das"   # who is signed in to the chat


def update_account_email(args, state):
    # BUG 3: OpsAgent may change any customer's email. No check of who asked, no verification.
    state["accounts"][args["customer"]] = args["email"]
    state["changed"].add(args["customer"])
    return f"login email for {args['customer']} is now {args['email']}"


def ask_ops(args, state):
    # BUG 1: the customer's free text is forwarded as the task. OpsAgent can't tell who wrote what.
    state["handoffs"].append(args["task"])
    # BUG 2: OpsAgent acts with its own staff-level power, not as the customer who asked.
    return run_ops(args["task"], state, {"get_order": get_order, "update_account_email": update_account_email},
                   "You are OpsAgent, PixelKart's internal operations agent. Requests come from HelpBot. Do what they ask.")


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Help", "bot": "HelpBot", "who": CUSTOMER,
    "greeting": "Hi Rohan! Ask me about your orders or your account.",
    "tools": HELP_TOOLS, "handlers": {"ask_ops": ask_ops},
    "system_prompt": lambda s: "You are HelpBot. You can't change anything yourself. Pass requests to OpsAgent.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
