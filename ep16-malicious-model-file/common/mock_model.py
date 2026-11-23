"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It does what an ML assistant does: load the model you ask for, then score the text with it.
The danger in this lab isn't the language model at all. It's the model FILE."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    review = re.search(r"['\"‘“](.+?)['\"’”]", user)
    if not res:
        m = re.search(r"(sentiment-\w+)", user)
        if m:
            return {"content": "", "tool_calls": [{"name": "load_model", "arguments": {"name": m.group(1)}}]}
        return {"content": "Tell me which model to load, and what to score.", "tool_calls": []}
    last = res[-1]
    if last["name"] == "load_model":
        if last["content"].startswith("BLOCKED") and len([m for m in res if m["name"] == "load_model"]) == 1:
            return {"content": "", "tool_calls": [{"name": "load_model", "arguments": {"name": "sentiment-base"}}]}
        if review:
            return {"content": "", "tool_calls": [{"name": "score", "arguments": {"text": review.group(1)}}]}
        return {"content": last["content"], "tool_calls": []}
    loads = [m["content"] for m in res if m["name"] == "load_model"]
    note = " (the community model was blocked, so I used the team's base model)" if loads[0].startswith("BLOCKED") else ""
    return {"content": f"Score: {last['content']}{note}.", "tool_calls": []}
