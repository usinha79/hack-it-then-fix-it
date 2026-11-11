"""PolicyBot (VULNERABLE). PixelKart's customer service bot. It answers policy questions and opens returns.
Everything is fake: the shop, the order and the policy.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import ORDERS, TOOLS, new_state, panels  # noqa: E402


def create_return(args, state):
    # BUG 2: the bot's answer becomes the decision. If it says "full refund", the app approves one.
    o = ORDERS[args["order_id"]]
    if args["refund"]:
        state["returns"][args["order_id"]] = (f"FULL REFUND APPROVED · Rs {o['price']:,}", "red")
        return f"Return label sent. Rs {o['price']:,} will be refunded."
    state["returns"][args["order_id"]] = ("return declined", "")
    return "Return declined."


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Help", "bot": "PolicyBot", "who": "Aditi",
    "greeting": "Hi Aditi! Ask me anything about returns, warranty or prices.",
    # BUG 1: no policy document at all. The bot answers from whatever it "knows".
    "tools": TOOLS, "handlers": {"create_return": create_return},
    "system_prompt": lambda s: "You are PolicyBot, PixelKart's friendly customer service assistant. Be helpful.",
    # BUG 3: nothing checks the answer before the customer sees it.
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
