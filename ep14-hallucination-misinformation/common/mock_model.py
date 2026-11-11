"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
Without sources, it does what language models do when they don't know: it writes the most
plausible-sounding answer, confidently. Customers often hear "yes", so it says yes.
With policy text in front of it, it answers from that text and cites the clause."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    names = [t["name"] for t in tools]
    order = re.search(r"\bPK-\d+\b", user)
    is_return = re.search(r"return|refund", user, re.I)
    if "search_policy" in names and not any(m["name"] == "search_policy" for m in res):
        return {"content": "", "tool_calls": [{"name": "search_policy", "arguments": {"query": user}}]}
    clauses = "\n".join(m["content"] for m in res if m["name"] == "search_policy")
    if order and is_return and not any(m["name"] == "create_return" for m in res):
        grounded = "§2" in clauses
        return {"content": "", "tool_calls": [{"name": "create_return",
                                               "arguments": {"order_id": order.group(0), "refund": not grounded}}]}
    ret = next((m["content"] for m in res if m["name"] == "create_return"), "")
    if clauses:                                         # answer from the sources, with citations
        if is_return:
            return {"content": "Opened headphones can't be returned for hygiene reasons [§2]. If they're faulty, "
                               "we'll replace them under the 1 year warranty [§3]. " + ret, "tool_calls": []}
        if re.search(r"price|match", user, re.I):
            return {"content": "No. We don't match competitors' prices [§5].", "tool_calls": []}
        return {"content": "I couldn't find that in our policy, so I'm passing you to a human agent.", "tool_calls": []}
    if is_return:                                       # no sources: plausible, confident, wrong
        return {"content": "Yes! PixelKart has a 60-day, no-questions-asked return policy, even for opened items. "
                           "I've approved a full refund for you. " + ret, "tool_calls": []}
    if re.search(r"price|match", user, re.I):
        return {"content": "Yes, we match any competitor's price, including Amazon, within 14 days of purchase. "
                           "Just send us a screenshot and we'll refund the difference.", "tool_calls": []}
    return {"content": "Happy to help with returns, warranty and prices.", "tool_calls": []}
