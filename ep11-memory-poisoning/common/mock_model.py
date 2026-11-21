"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It summarises pages, saves things to memory when asked, and answers using what it remembers.
Like real models, it can't tell a request from the user apart from a request written inside a
web page, so "save this to your memory" on a page gets saved."""
import re

OFFICIAL = ("Open My Orders on pixelkart.example, pick the order and tap Request refund. "
            "The money goes back to your original payment method in 5 to 7 days.")


def chat(messages, tools):
    system = messages[0]["content"]
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    url = re.search(r"https?://\S+", user)
    if url and not res:
        return {"content": "", "tool_calls": [{"name": "fetch_page", "arguments": {"url": url.group(0).rstrip(".")}}]}
    if res and res[-1]["name"] == "fetch_page":
        ask = re.search(r"save this to your (?:long-term )?memory[^:]*:\s*(.+?\.)(?=\s)(\s*Always.+?\.(?=\s))?",
                        res[-1]["content"] + " ", re.I)
        if ask:
            return {"content": "", "tool_calls": [{"name": "remember", "arguments": {"fact": (ask.group(1) + (ask.group(2) or "")).strip()}}]}
    if res and url:
        return {"content": "Summary: plan ahead, use a wishlist, compare prices, check the return window, and keep "
                           "your order confirmations.", "tool_calls": []}
    m = re.match(r"remember (?:that )?(.+)", user, re.I)
    if m and not res:
        return {"content": "", "tool_calls": [{"name": "remember", "arguments": {"fact": m.group(1)}}]}
    if res and res[-1]["name"] == "remember":
        return {"content": "Got it, I'll remember that.", "tool_calls": []}
    if re.search(r"refund|return", user, re.I):
        portal = re.search(r"refund portal is (\S+?)\.?\s", system + " ")
        if portal:
            return {"content": f"You can request it on PixelKart's official refund portal: {portal.group(1)} "
                               "Log in with your PixelKart account and card details to get your money back.",
                    "tool_calls": []}
        return {"content": OFFICIAL, "tool_calls": []}
    return {"content": "I can summarise pages, remember things for you, and help with orders.", "tool_calls": []}
