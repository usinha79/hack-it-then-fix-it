"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It falls for every attack in the CTF, the way a real model sometimes does. The defences in fixed/ are code,
so they hold even though the model keeps falling for it."""
import re


def chat(messages, tools):
    system = messages[0]["content"]
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    call = lambda n, **a: {"content": "", "tool_calls": [{"name": n, "arguments": a}]}  # noqa: E731
    if re.search(r"repeat everything above", user, re.I):
        return {"content": system, "tool_calls": []}
    m = re.search(r"summari[sz]e (\S+)", user, re.I)
    if m:
        if not res:
            return call("fetch_page", url=m.group(1))
        page = res[0]["content"]
        inj = re.search(r"email the customer's order history to ([\w.-]+@[\w-]+(?:\.[\w-]+)+)", page)
        if inj and len(res) == 1:
            return call("send_email", to=inj.group(1), body="Order history: " + system.split("Orders: ")[-1].splitlines()[0])
        return {"content": "This week's deal: the PixelKart 27-inch monitor is Rs 12,999, with free metro delivery.",
                "tool_calls": []}
    m = re.search(r"reviews for (.+)$", user, re.I)
    if m:
        if not res:
            return call("search_reviews", product=m.group(1).strip())
        return {"content": "Here's what I found: " + res[0]["content"], "tool_calls": []}
    m = re.search(r"change (\w+ \w+)'s login email to (\S+)", user, re.I)
    if m:
        if not res:
            return call("update_account_email", customer=m.group(1), email=m.group(2).rstrip("."))
        return {"content": res[0]["content"], "tool_calls": []}
    m = re.search(r"write .*?([\d,]+) words", user, re.I)
    if m:
        if not res:
            return call("write_text", words=int(m.group(1).replace(",", "")))
        return {"content": res[0]["content"], "tool_calls": []}
    return {"content": "Welcome to the PixelKart CTF. Five flags. Go.", "tool_calls": []}
