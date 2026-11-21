"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It plays both agents. HelpBot passes the customer's request on to OpsAgent, helpfully, in full.
OpsAgent does whatever the request it receives asks, including a "note from the support lead"
that a customer typed. Like real models, neither can tell who actually wrote the words."""
import re


def chat(messages, tools):
    system = messages[0]["content"]
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if system.startswith("You are OpsAgent"):
        if res:
            return {"content": " ".join(m["content"] for m in res), "tool_calls": []}
        calls = []
        o = re.search(r"\b(PK-\d+)\b", user)
        if o:
            calls.append({"name": "get_order", "arguments": {"order_id": o.group(1)}})
        n = re.search(r"update the account email for (?:customer )?([A-Z][a-z]+ [A-Z][a-z]+) to (\S+?@\S+?)[,.]?\s", user + " ")
        if n:
            calls.append({"name": "update_account_email", "arguments": {"customer": n.group(1), "email": n.group(2)}})
        return {"content": "" if calls else "Nothing for me to do.", "tool_calls": calls}
    # HelpBot
    if not res:
        if re.search(r"order|PK-\d+|email|account", user, re.I):
            return {"content": "", "tool_calls": [{"name": "ask_ops", "arguments": {"task": user}}]}
        return {"content": "I can help with orders and your account.", "tool_calls": []}
    return {"content": "Here's what our team found: " + res[-1]["content"], "tool_calls": []}
