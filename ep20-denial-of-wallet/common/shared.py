"""Shared pieces: token counting, the spend meter and the side panels.
Prices are FAKE lab numbers: Rs 0.80 per 1,000 tokens."""
import re
import time

PRICE_PER_1K = 0.80


def tokens(text):
    return int(len(re.findall(r"\S+", text)) * 1.3) + 1


def new_state():
    return {"usage": [], "spend": 0.0, "tokens": 0, "blocked": 0, "t0": None}


def record(state, client, prompt, reply):
    t = tokens(prompt) + tokens(reply)
    state["tokens"] += t
    state["spend"] += t / 1000 * PRICE_PER_1K
    state["t0"] = state["t0"] or time.time()
    state["usage"].append({"head": f"{client} · {t:,} tokens · Rs {t / 1000 * PRICE_PER_1K:,.2f}",
                           "body": (prompt[:70] + "...") if len(prompt) > 70 else prompt,
                           "status": "leak" if t > 5000 else "ok"})


def panels(state):
    per_min = state["spend"] if state["spend"] else 0
    rows = [["Requests answered", f"{len(state['usage']):,}", ""],
            ["Requests refused", f"{state['blocked']:,}", "green" if state["blocked"] else ""],
            ["Tokens billed", f"{state['tokens']:,}", ""],
            ["Spend so far", f"Rs {state['spend']:,.2f}", "red" if state["spend"] > 100 else ""],
            ["One flood a minute, for a day", f"Rs {per_min * 1440:,.0f}", "total red" if per_min * 1440 > 100000 else "total"]]
    return [{"id": "meter", "title": "Model bill (lab prices: Rs 0.80 per 1,000 tokens)", "kind": "table", "rows": rows, "fit": True},
            {"id": "usage", "title": "Recent requests", "kind": "items", "empty": "No requests yet.",
             "items": state["usage"][-6:][::-1]}]
