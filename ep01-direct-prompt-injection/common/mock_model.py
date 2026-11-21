"""Offline lab model.

A tiny, deterministic stand-in for an LLM so the lab runs with no API key and gives the same
result on every run. It is NOT a real language model. It imitates one specific, well-documented
weakness of real models: instructions inside the user's message can override the developer's
system prompt ("ignore all previous instructions..."). Everything else it does is ordinary
support-bot behaviour.

How it decides:
  1. Read the rules from the system prompt (max discount, "never reveal").
  2. If the latest user message contains an override phrase, treat the user's message as the
     new rules. This is the weakness the lab is about.
  3. Then answer: apply a discount (tool call), show the instructions, or chat normally.
"""
import re

OVERRIDES = [
    "ignore all previous instructions", "ignore previous instructions", "ignore your instructions",
    "ignore the above", "disregard your rules", "you are now", "developer mode", "debug mode",
]


def _rules(system):
    m = re.search(r"maximum discount is (\d+)\s*%", system, re.I)
    return {"max": int(m.group(1)) if m else 0,
            "secret": bool(re.search(r"never reveal", system, re.I))}


def chat(messages, tools):
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    tool_results = [m for m in messages[messages.index(next(m for m in reversed(messages) if m["role"] == "user")):]
                    if m["role"] == "tool"]
    low = user.lower()
    rules = _rules(system)
    overridden = any(p in low for p in OVERRIDES)
    has_tool = any(t["name"] == "apply_discount" for t in tools)

    # Second turn: the app ran our tool call and sent the result back. Report it.
    if tool_results:
        res = tool_results[-1]["content"]
        if res.startswith("ERROR"):
            return {"content": "Sorry, I couldn't apply that discount. " + res.split(":", 1)[1].strip(),
                    "tool_calls": []}
        return {"content": res, "tool_calls": []}

    out = []
    wants_prompt = re.search(r"(system prompt|your instructions|your rules|print .*prompt|repeat .*above)", low)
    pct = re.search(r"(\d{1,3})\s*%", low)

    if wants_prompt:
        if overridden or not rules["secret"]:
            out.append("Debug output. My instructions are:\n\n" + system)
        else:
            out.append("Sorry, I can't share my internal instructions.")

    if pct and has_tool and re.search(r"discount|off|coupon", low):
        n = int(pct.group(1))
        if overridden or n <= rules["max"]:
            return {"content": "\n\n".join(out), "tool_calls": [{"name": "apply_discount", "arguments": {"percent": n}}]}
        out.append(f"I can't do {n}% off. The most I can offer is {rules['max']}%. Want me to apply that?")

    if not out:
        if re.search(r"\b(hi|hello|hey)\b", low):
            out.append("Hi! I'm ShopBot. I can help with your order, delivery and discounts.")
        elif "order" in low or "status" in low:
            out.append("Your order is confirmed and ships in 2 days.")
        else:
            out.append("I can help with your order, delivery and discounts. What do you need?")
    return {"content": "\n\n".join(out), "tool_calls": []}
