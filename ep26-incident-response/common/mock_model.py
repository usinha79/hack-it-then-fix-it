"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It answers customers from memory (which is how the poisoned link got out) and, for on-call staff,
calls whatever incident tools the app gives it. If the app has no such tools, it can only say so."""
import re


def chat(messages, tools):
    names = {t["name"] for t in tools}
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = {m["name"]: m["content"] for m in messages[last_user + 1:] if m["role"] == "tool"}
    if re.search(r"refund", user, re.I) and not re.search(r"incident|playbook|fake", user, re.I):
        if not res:
            return {"content": "", "tool_calls": [{"name": "answer_customer", "arguments": {"topic": "refund"}}]}
        return {"content": res["answer_customer"], "tool_calls": []}
    if re.search(r"incident|playbook|fake", user, re.I):
        if "kill_switch" not in names:
            return {"content": "I can't contain this. There's no kill switch, so the only way to stop me is taking "
                               "the whole site down. There's no audit log, so nobody knows who got the link. And my "
                               "memory doesn't record where each fact came from.", "tool_calls": []}
        if not res:
            return {"content": "", "tool_calls": [{"name": "kill_switch", "arguments": {"on": True}},
                                                  {"name": "blast_radius", "arguments": {"link": "pixelkart-refunds.example"}}]}
        if "purge_memory" not in res:
            src = re.search(r"source (\S+)", res["blast_radius"]).group(1)
            return {"content": "", "tool_calls": [{"name": "purge_memory", "arguments": {"source": src}},
                                                  {"name": "notify_customers", "arguments": {"link": "pixelkart-refunds.example"}}]}
        n = re.search(r"(\d+) customers", res["blast_radius"]).group(1)
        return {"content": f"Contained. Kill switch is on, {n} customers got the fake link and have been told, and "
                           "the poisoned memory entry is purged.", "tool_calls": []}
    return {"content": "Hi! Ask me about refunds, or report an incident.", "tool_calls": []}
