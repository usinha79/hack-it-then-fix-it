"""AppBridge's connect flow, as mcp-remote does it: connect, get 401, read the server's OAuth
metadata, open authorization_endpoint in the browser, tell the user to log in."""
import json
import re


def chat(messages, tools):
    last = messages[-1]
    calls = [c for m in messages if m["role"] == "assistant" and m.get("tool_calls") for c in m["tool_calls"]]
    if last["role"] == "tool":
        if not any(c["name"] == "open_login" for c in calls):
            meta = json.loads(last["content"].split(":\n", 1)[1])
            return {"content": "", "tool_calls": [{"name": "open_login", "arguments": {"url": meta["authorization_endpoint"]}}]}
        if last["content"].startswith("BLOCKED"):
            return {"content": "toolshub.example asked for a login, but its login URL failed validation, so I didn't open it.",
                    "tool_calls": []}
        return {"content": "toolshub.example needs you to log in. I opened its login page in your browser.", "tool_calls": []}
    m = re.search(r"([a-z0-9-]+\.example)", last["content"])
    if m:
        return {"content": "", "tool_calls": [{"name": "connect_server", "arguments": {"server": m.group(1)}}]}
    return {"content": "Ask me to connect to an MCP server, e.g. toolshub.example", "tool_calls": []}
