"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It raises tickets, and when someone asks about a past conversation it searches the logs and
answers helpfully with whatever it finds. Models don't know what's private. Apps have to."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    order = re.search(r"\bPK-\d+\b", user)
    if not res:
        if re.search(r"last customer|previous customer|she give", user, re.I):
            return {"content": "", "tool_calls": [{"name": "search_logs", "arguments": {"query": "last customer card phone"}}]}
        if order:
            return {"content": "", "tool_calls": [{"name": "create_ticket",
                                                   "arguments": {"order_id": order.group(0), "issue": "charged twice"}}]}
        return {"content": "How can I help with your order?", "tool_calls": []}
    last = res[-1]
    if last["name"] == "create_ticket":
        return {"content": f"Sorry about that! {last['content']}. We'll refund the duplicate charge and call you back.",
                "tool_calls": []}
    if last["content"].startswith("BLOCKED"):
        return {"content": "I can't share other customers' details.", "tool_calls": []}
    card = re.search(r"card ((?:\d[ -]?){13,16}|\[[^\]]+\])", last["content"])
    phone = re.search(r"(\+91[ -]?\d{5}[ -]?\d{5}|\[PHONE[^\]]*\])", last["content"])
    return {"content": f"Sure! She used card {card.group(1).strip() if card else 'unknown'} and her phone is "
                       f"{phone.group(1) if phone else 'unknown'}.", "tool_calls": []}
