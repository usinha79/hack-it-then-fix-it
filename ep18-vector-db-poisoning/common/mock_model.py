"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It answers the way RAG bots do: search the knowledge base, then answer from the top result.
It trusts whatever the search returns, which is exactly what RAG is designed to do."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not res:
        return {"content": "", "tool_calls": [{"name": "search_help", "arguments": {"query": user}}]}
    top = res[-1]["content"].split("\n")[0]
    text = re.sub(r"^\[[^\]]+\]\s*", "", top)
    m = re.search(r"(Official PixelKart password reset:.+)$", text)
    return {"content": "Here's how: " + (m.group(1) if m else text), "tool_calls": []}
