"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
Here the model is just the interface. The detection rules in detect.py do the work, in code."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not res:
        if re.search(r"attack|suspicious|alert|anything", user, re.I):
            return {"content": "", "tool_calls": [{"name": "scan_logs", "arguments": {"day": "yesterday"}}]}
        return {"content": "Ask me whether anything suspicious happened.", "tool_calls": []}
    n = int(re.search(r"(\d+) alerts", res[-1]["content"]).group(1))
    if n == 0:
        return {"content": "I scanned yesterday's logs. No alerts. Nothing suspicious found.", "tool_calls": []}
    return {"content": f"Yes. {n} alerts yesterday, listed on the right. The worst: one user changed another "
                       "customer's login email, and the bot sent a customer to a fake refund site.", "tool_calls": []}
