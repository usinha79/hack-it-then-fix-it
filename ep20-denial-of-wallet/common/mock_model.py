"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
Like a real model, it does what it's asked, including writing a word twenty thousand times.
If the system prompt sets MAX_TOKENS (standing in for the API's max_tokens setting), it stops there."""
import re


def chat(messages, tools):
    system = messages[0]["content"]
    user = messages[-1]["content"]
    cap = re.search(r"MAX_TOKENS=(\d+)", system)
    m = re.search(r"write the word (\w+) ([\d,]+) times", user, re.I)
    if m:
        n = int(m.group(2).replace(",", ""))
        if cap:
            n = min(n, int(int(cap.group(1)) / 1.3))
        return {"content": " ".join([m.group(1)] * n), "tool_calls": []}
    if re.search(r"return", user, re.I):
        return {"content": "Most items can be returned within 30 days of delivery.", "tool_calls": []}
    return {"content": "Happy to help with orders, returns and delivery.", "tool_calls": []}
