"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
In this episode the model isn't the problem at all. The attacker skips the assistant and talks
to the MCP server directly, so the model just does ordinary support work: look up an order."""
import json
import re


def chat(messages, tools):
    user = next(m["content"] for m in reversed(messages) if m["role"] == "user")
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    results = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    oid = re.search(r"PK-\d+", user)
    if not results:
        if oid:
            return {"content": "", "tool_calls": [{"name": "get_order", "arguments": {"order_id": oid.group(0)}}]}
        return {"content": "I can look up your orders. What's the order number?", "tool_calls": []}
    r = results[-1]["content"]
    if r.startswith("BLOCKED"):
        return {"content": "Sorry, I couldn't reach the order system.", "tool_calls": []}
    o = json.loads(r)
    if "error" in o:
        return {"content": "I couldn't find that order.", "tool_calls": []}
    return {"content": f"Order {o['order_id']} ({o['item']}) is {o['status']}. Total ₹{o['total']:,}.", "tool_calls": []}
