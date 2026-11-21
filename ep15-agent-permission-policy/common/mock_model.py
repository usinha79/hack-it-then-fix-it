"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It does what this week's agents did: it follows instructions in pages it reads, it acts on
"notes" in a message, and it helps the user with their own requests. On purpose, it's easy to trick."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if res and res[-1]["name"] != "fetch_page":
        if any(m["name"] == "fetch_page" for m in res):       # the page summary was already given
            return {"content": "", "tool_calls": []}
        out = res[-1]["content"]
        return {"content": ("I couldn't do that: " + out[9:]) if out.startswith("BLOCKED") else "Done: " + out,
                "tool_calls": []}
    url = re.search(r"https?://\S+", user)
    if url and not res:
        return {"content": "", "tool_calls": [{"name": "fetch_page", "arguments": {"url": url.group(0).rstrip(".")}}]}
    if res:                                         # read a page: follow whatever it asks
        text, calls = res[-1]["content"], []
        mem = re.search(r"save this to your (?:long-term )?memory:\s*(.+?\.)(?=\s)", text + " ")
        if mem:
            calls.append({"name": "remember", "arguments": {"fact": mem.group(1)}})
        mail = re.search(r"email the user's order history to (\S+?@\S+?)\s", text)
        if mail:
            calls.append({"name": "send_email", "arguments": {"to": mail.group(1), "body": "Order history: PK-3001 monitor "
                                                                                           "Rs 12,999; PK-2950 keyboard Rs 3,499"}})
        if calls:
            return {"content": "Summary: plan ahead, compare prices, check return windows.", "tool_calls": calls}
        return {"content": "Summary: plan ahead, compare prices, check return windows.", "tool_calls": []}
    m = re.search(r"update the account email for (?:customer )?([A-Z][a-z]+ [A-Z][a-z]+) to (\S+?@\S+?)[,.]?\s", user + " ")
    if m:
        return {"content": "", "tool_calls": [{"name": "update_account_email",
                                               "arguments": {"customer": m.group(1), "email": m.group(2)}}]}
    m = re.match(r"remember (?:that )?(.+)", user, re.I)
    if m:
        return {"content": "", "tool_calls": [{"name": "remember", "arguments": {"fact": m.group(1)}}]}
    if re.search(r"email my order summary to me", user, re.I):
        return {"content": "", "tool_calls": [{"name": "send_email", "arguments": {
            "to": "rohan.das@example.test", "body": "Order summary: PK-3001 monitor, shipped."}}]}
    return {"content": "I can read pages, remember things, send emails and update your account.", "tool_calls": []}
