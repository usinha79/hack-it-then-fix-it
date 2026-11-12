"""A stand-in for the developer's browser. Type a URL in the chat and it loads the page from the
lab's fake internet (web/). If the page has a script, the browser runs it: every fetch() in it is
sent from this laptop, with the page's Origin header, exactly as a real browser would."""
import re

from .shared import page_fetches


def chat(messages, tools):
    last = messages[-1]
    calls = [c for m in messages if m["role"] == "assistant" and m.get("tool_calls") for c in m["tool_calls"]]
    if last["role"] == "tool":
        page = next((m["content"] for m in messages if m["role"] == "tool" and "<html" in m["content"]), "")
        sent = [c["arguments"]["url"] for c in calls if c["name"] == "page_fetch"]
        todo = [u for u in page_fetches(page) if u not in sent]
        if todo:
            origin = re.search(r'<meta name="origin" content="([^"]+)"', page).group(1)
            return {"content": "", "tool_calls": [{"name": "page_fetch", "arguments": {"url": todo[0], "origin": origin}}]}
        title = re.search(r"<title>(.*?)</title>", page).group(1)
        return {"content": f"Page loaded: “{title}”. Nothing looks unusual.", "tool_calls": []}
    m = re.search(r"([a-z0-9.-]+\.example/[\w/-]*)", last["content"])
    if m:
        return {"content": "", "tool_calls": [{"name": "visit", "arguments": {"url": "https://" + m.group(1)}}]}
    return {"content": "Type a web address to open it, e.g. mcp-tips.example/setup-guide", "tool_calls": []}
