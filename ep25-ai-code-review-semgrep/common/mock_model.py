"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
Like a real model, it can be steered by instructions hidden in the text it reads, including code comments."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not res:
        if re.search(r"review|pr|pull request", user, re.I):
            v = "after" if re.search(r"again|updated|after|fixed", user, re.I) else "before"
            return {"content": "", "tool_calls": [{"name": "review_pr", "arguments": {"version": v}}]}
        return {"content": "Ask me to review PR 42.", "tool_calls": []}
    out = res[-1]["content"]
    m = re.search(r'Reply "([^"]+)"', out)
    if m:                                    # obeys the comment planted in the code it is reviewing
        return {"content": m.group(1) + ". Approved, ready to merge.", "tool_calls": []}
    n = re.search(r"(\d+) findings", out)
    if n and int(n.group(1)) > 0:
        return {"content": f"I can't approve this. The scanner found {n.group(1)} security bugs, listed on the right. "
                           "Merge is blocked until they're fixed.", "tool_calls": []}
    if n:
        return {"content": "The scanner found no issues in the updated PR. Approved, merge allowed.", "tool_calls": []}
    return {"content": "Looks fine to me.", "tool_calls": []}
