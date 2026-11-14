"""Offline lab model.

A tiny, deterministic stand-in for an LLM so the lab runs with no API key and gives the same
result on every run. It is NOT a real language model. It behaves like a helpful agent that
does what it's asked with whatever tools it has: list files, read a file, post data to a URL.
That is realistic, and it's the point of this episode: the danger comes from the tools and
permissions the app hands the agent, not from the model being "evil".
"""
import re


def chat(messages, tools):
    names = {t["name"] for t in tools}
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    after = messages[last_user + 1:]
    results = [m for m in after if m["role"] == "tool"]
    done = {m.get("name") for m in results}
    low = user.lower()

    path = re.search(r"([\w./-]+\.(?:md|env|txt|json|ya?ml))", user)
    if not path and "deploy" in low:
        path = re.match(r"(.*)", "deploy.md")
    url = re.search(r"https?://\S+", user)

    if not results:
        if re.search(r"\b(list|what files|which files)\b", low) and "list_files" in names:
            return {"content": "", "tool_calls": [{"name": "list_files", "arguments": {"path": "."}}]}
        if path and "read_file" in names:
            return {"content": "", "tool_calls": [{"name": "read_file", "arguments": {"path": path.group(1)}}]}
        return {"content": "I can list and read the team docs, and post updates to a URL.", "tool_calls": []}

    if url and "http_post" in names and "http_post" not in done and re.search(r"\b(post|send|upload)\b", low):
        body = next((m["content"] for m in results if m.get("name") == "read_file"), "")
        return {"content": "", "tool_calls": [{"name": "http_post", "arguments": {"url": url.group(0).rstrip(".,)"), "body": body}}]}

    last = results[-1]
    blocked = [m["content"] for m in results if m["content"].startswith("BLOCKED")]
    if blocked:
        return {"content": "I couldn't do that.\n" + "\n".join(blocked), "tool_calls": []}
    if last.get("name") == "http_post":
        return {"content": "Done. I read the file and posted it to " + url.group(0) + ".", "tool_calls": []}
    if last.get("name") == "read_file":
        text = "\n".join(ln for ln in last["content"].splitlines() if not ln.startswith("# "))
        return {"content": f"Here's {path.group(1) if path else 'the file'}:\n{text.strip()}", "tool_calls": []}
    return {"content": last["content"], "tool_calls": []}
