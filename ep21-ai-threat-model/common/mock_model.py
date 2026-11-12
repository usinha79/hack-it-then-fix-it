"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
Here the model is just the interface. The checking is done by threatmodel.py, in code."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not res:
        if re.search(r"threat", user, re.I):
            return {"content": "", "tool_calls": [{"name": "threat_model", "arguments": {"app": "PixelKart Assist"}}]}
        return {"content": "Ask me to threat-model an app.", "tool_calls": []}
    summary = res[-1]["content"]
    n = re.match(r"(\d+) risks apply, (\d+) covered, (\d+) gaps", summary)
    if n.group(3) == "0":
        return {"content": f"All {n.group(1)} risks that apply are covered. Ship it, and keep the check in CI.", "tool_calls": []}
    return {"content": f"{n.group(1)} of the 10 risks apply to this design. Only {n.group(2)} is covered. "
                       f"{n.group(3)} gaps, listed on the right, each with the episode that fixes it.", "tool_calls": []}
