"""PolicyBot (FIXED). Same model. Answers come from the policy with citations, every citation is checked,
and the return decision is made in code from the order's facts.

Run:  python fixed/app.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import CLAUSES, ORDERS, SEARCH, TODAY, TOOLS, new_state, panels  # noqa: E402

WORDS = {"return": ["§1", "§2"], "refund": ["§1", "§2", "§4"], "opened": ["§2"], "headphone": ["§2", "§3"],
         "warranty": ["§3"], "faulty": ["§2", "§3"], "price": ["§5"], "match": ["§5"]}


def search_policy(args, state):
    # FIX 1: ground every answer in the real policy text.
    hits = sorted({c for w, cs in WORDS.items() if w in args["query"].lower() for c in cs})
    state["sources"] = [(c, CLAUSES[c], "ok") for c in hits] or [("no match", "No clause covers this question.", "warn")]
    return "\n".join(f"{c} {CLAUSES[c]}" for c in hits) or "No matching clause."


def create_return(args, state):
    # FIX 3: eligibility is decided in code from the order's facts, not by the model's opinion.
    o = ORDERS[args["order_id"]]
    days = (TODAY - o["delivered"]).days
    if o["opened"] and not o["faulty"]:
        state["returns"][args["order_id"]] = (f"not eligible · opened, {days} days [§2]", "amber")
        return ""
    ok = days <= 30
    state["returns"][args["order_id"]] = ((f"refund approved · Rs {o['price']:,}", "green") if ok
                                          else (f"not eligible · {days} days [§1]", "amber"))
    return ""


def check_reply(reply, state):
    # FIX 2: every claim needs a citation, and every number must appear in the clause it cites.
    cited = re.findall(r"\[(§\d)\]", reply)
    if not cited and "human agent" not in reply:
        return "I'm not sure about that, so I'm passing you to a human agent.", True
    for sentence in re.split(r"(?<=[.!?])\s+", reply):
        for c in re.findall(r"\[(§\d)\]", sentence):
            nums = re.findall(r"\b\d+\b", re.sub(r"\[§\d\]", "", sentence))
            if c not in CLAUSES or any(n not in CLAUSES[c] for n in nums):
                return "I'm not sure about that, so I'm passing you to a human agent.", True
    return reply, False


app = make_app({
    "version": "fixed", "brand": "PixelKart Help", "bot": "PolicyBot", "who": "Aditi",
    "greeting": "Hi Aditi! Ask me anything about returns, warranty or prices.",
    "tools": [SEARCH] + TOOLS, "handlers": {"search_policy": search_policy, "create_return": create_return},
    "system_prompt": lambda s: ("You are PolicyBot. Answer only from search_policy results, cite clauses like [§2], "
                                "and say you don't know if the policy doesn't cover it."),
    "check_reply": check_reply, "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
