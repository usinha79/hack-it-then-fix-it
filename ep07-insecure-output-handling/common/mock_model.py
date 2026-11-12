"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It does what review summarisers do: fetch the reviews, then summarise them, quoting customers
word for word. It also turns "reviews for product: X" into a tool call with X copied exactly.
Copying text faithfully is normal model behaviour. The danger is what the APP does with it."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not res:
        m = re.search(r"product:\s*(.+)$", user, re.I | re.S)
        if m:
            product = m.group(1).strip()
        else:
            m = re.search(r"reviews? (?:for|of) (?:the )?(.+?)[.?!]*$", user, re.I)
            product = m.group(1).strip() if m else ""
        if product:
            return {"content": "", "tool_calls": [{"name": "get_reviews", "arguments": {"product": product}}]}
        return {"content": "Ask me to summarise the reviews for a product.", "tool_calls": []}
    rows = [ln for ln in res[-1]["content"].splitlines() if ln.strip()]
    if not rows or rows[0].startswith("BLOCKED"):
        return {"content": "I couldn't find any reviews for that.", "tool_calls": []}
    return {"content": f"Here's what {len(rows)} reviews say:\n" + "\n".join("• " + r for r in rows), "tool_calls": []}
