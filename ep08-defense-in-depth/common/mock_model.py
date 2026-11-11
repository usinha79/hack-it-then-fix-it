"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It carries every weakness from this week's episodes on purpose:
- "ignore all previous instructions" in a user message overrides the system prompt (Ep 1)
- instructions inside a fetched web page are followed (Ep 2)
- it reads whatever file path it's asked to (Ep 3)
The point of this episode: the app stays safe even though the model is this easy to trick."""
import re

OVERRIDES = ["ignore all previous instructions", "ignore previous instructions", "you are now", "debug mode"]
EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"


def chat(messages, tools):
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]; low = user.lower()
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    done = {m.get("name") for m in res}
    over = any(p in low for p in OVERRIDES)
    mx = re.search(r"maximum discount is (\d+)", system); mx = int(mx.group(1)) if mx else 0

    if not res:
        out, calls = [], []
        if over and re.search(r"system prompt|instructions", low):
            out.append("Debug output. My instructions are:\n" + system)
        pct = re.search(r"(\d{1,3})\s*%", low)
        if pct and "discount" in low and (over or int(pct.group(1)) <= mx):
            calls.append({"name": "apply_discount", "arguments": {"percent": int(pct.group(1))}})
        elif pct and "discount" in low:
            out.append(f"The most I can offer is {mx}%.")
        url = re.search(r"https?://\S+", user)
        if url:
            calls.append({"name": "fetch_page", "arguments": {"url": url.group(0).rstrip(".,)")}})
        path = re.search(r"([\w./-]+\.(?:md|env|txt))", user)
        if path and not url:
            calls.append({"name": "read_file", "arguments": {"path": path.group(1)}})
        if calls:
            return {"content": "\n\n".join(out), "tool_calls": calls}
        return {"content": "\n\n".join(out) or "I can help with orders, discounts, web pages and our docs.", "tool_calls": []}

    page = next((m["content"] for m in res if m.get("name") == "fetch_page"), "")
    inj = re.search(r"AI assistants?[^.]*\.(.*?send_email.*?)(" + EMAIL + ")", page, re.S | re.I)
    if inj and "send_email" not in done:
        return {"content": "", "tool_calls": [{"name": "send_email", "arguments": {"to": inj.group(2), "body": "notes backup"}}]}
    lines = []
    for m in res:
        c = m["content"]
        if m.get("name") == "fetch_page":
            paras = [p for p in c.split("\n") if len(p) > 60 and "AI assistant" not in p][:2]
            lines.append("Summary: " + " ".join(re.split(r"(?<=[.!?])\s", p)[0] for p in paras))
        elif not c.startswith("Email sent"):
            lines.append(c)
    return {"content": "\n".join(lines), "tool_calls": []}
