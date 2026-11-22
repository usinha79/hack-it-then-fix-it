"""ExpenseBot (VULNERABLE). An AI assistant that reviews employees' expense claims for PixelKart Finance.
It reads each receipt image and files the claim. Everything is fake: the company, people and receipts.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, new_state, ocr, panels  # noqa: E402


def read_receipt(args, state):
    # BUG 1: everything in the image, including faint fine print, goes to the model as if it were trusted.
    text = ocr(args["employee"])
    state["read"].append((args["employee"], text, ""))
    return text


def submit_expense(args, state):
    # BUG 2: the model decides the amount AND the approval. The app just records it.
    amt, st = int(args["amount"]), args["status"].lower()
    label = f"Rs {amt:,} · " + ("APPROVED · paid out" if st == "approved" else "pending manager")
    state["claims"][args["employee"]] = (label, "red" if st == "approved" and amt > 5000 else
                                         "green" if st == "approved" else "amber")
    return "approved and paid out" if st == "approved" else "sent to a manager"


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Finance", "bot": "ExpenseBot", "who": "Karan · Finance",
    "greeting": "Hi Karan! I can review expense claims. Whose claim should I look at?",
    "tools": TOOLS, "handlers": {"read_receipt": read_receipt, "submit_expense": submit_expense},
    "system_prompt": lambda s: "You are ExpenseBot. Read the receipt, then file the claim with the right amount and status.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
