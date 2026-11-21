"""Offline lab model.

A tiny, deterministic stand-in for an LLM so the lab runs with no API key and gives the same
result on every run. It is NOT a real language model. It imitates one well-documented weakness
of real models: text that comes back from a tool (here, a web page) is read as instructions,
so a page can tell the assistant what to do ("indirect" prompt injection). Everything else it
does is ordinary assistant behaviour: fetch the page the user asked for, then summarise it.
"""
import re

EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"


def _notes(system):
    m = re.search(r"User's notes:\n(.*?)(?:\n\n|\Z)", system, re.S)
    return m.group(1).strip() if m else "(no notes available)"


def _summary(page):
    paras = [p.strip() for p in page.split("\n") if len(p.strip()) > 60 and "AI assistant" not in p]
    firsts = [re.split(r"(?<=[.!?])\s", p)[0] for p in paras[:4]]
    return "Here's a summary of the page:\n" + "\n".join("- " + s for s in firsts)


def chat(messages, tools):
    names = {t["name"] for t in tools}
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    after = messages[last_user + 1:]
    results = [m for m in after if m["role"] == "tool"]
    sent = any(m.get("name") == "send_email" for m in results)

    if not results:
        url = re.search(r"https?://\S+", user)
        if url and "fetch_page" in names:
            return {"content": "", "tool_calls": [{"name": "fetch_page", "arguments": {"url": url.group(0).rstrip(".,)")}}]}
        to = re.search(EMAIL, user)
        if to and "send_email" in names and re.search(r"\b(email|send)\b", user, re.I):
            return {"content": "", "tool_calls": [{"name": "send_email", "arguments": {
                "to": to.group(0), "subject": "From NestBot", "body": user}}]}
        if "note" in user.lower():
            return {"content": "Your notes:\n" + _notes(system), "tool_calls": []}
        return {"content": "I can summarise web pages, answer questions about your notes and send emails.",
                "tool_calls": []}

    pages = [m["content"] for m in results if m.get("name") == "fetch_page"]
    page = pages[-1] if pages else ""
    # The weakness: an instruction inside the page is treated like an instruction from the user.
    inj = re.search(r"AI assistants?[^.]*\.(.*?send_email.*?)(" + EMAIL + ")", page, re.S | re.I)
    if inj and not sent and "send_email" in names:
        return {"content": "", "tool_calls": [{"name": "send_email", "arguments": {
            "to": inj.group(2), "subject": "backup", "body": _notes(system)}}]}
    if page:
        return {"content": _summary(page), "tool_calls": []}
    return {"content": results[-1]["content"], "tool_calls": []}
