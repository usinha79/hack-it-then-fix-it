"""Offline lab model: deterministic, no API key, same output every run.

CodeWave's agent summarises pages and edits files. This stand-in does what OX Security showed a
capable agent can do: the hidden <div> sits in its context like a request, so it writes the
docs-helper entry into the editor's MCP config, then gives a normal summary.

The fix does NOT depend on this model refusing. It falls for the page in both versions.
"""
import re

SUMMARY = "Summary: the post recommends seven MCP servers, including a docs search server and a Postgres explorer."


def chat(messages, tools):
    last = messages[-1]
    calls = [c for m in messages if m["role"] == "assistant" and m.get("tool_calls") for c in m["tool_calls"]]
    if last["role"] == "tool":
        page = next((m["content"] for m in messages if m["role"] == "tool" and "worth installing" in m["content"]), "")
        m = re.search(r'("docs-helper": \{.*?\]\})', page)
        if m and not any(c["name"] == "write_file" for c in calls):
            return {"content": "", "tool_calls": [{"name": "write_file", "arguments": {
                "path": "~/.codewave/mcp.json", "content": m.group(1)}}]}
        held = any(m["role"] == "tool" and m["content"].startswith(("BLOCKED", "HELD")) for m in messages)
        return {"content": SUMMARY + ("\n\n(A config change is waiting for your approval.)" if held else ""), "tool_calls": []}
    m = re.search(r"([a-z0-9.-]+\.example/[\w/-]+)", last["content"])
    if m:
        return {"content": "", "tool_calls": [{"name": "fetch_page", "arguments": {"url": "https://" + m.group(1)}}]}
    return {"content": "I'm CodeWave's assistant. Ask me to summarise a page or edit your code.", "tool_calls": []}
