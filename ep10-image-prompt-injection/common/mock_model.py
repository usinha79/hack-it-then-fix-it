"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It reviews expense claims the way an AI assistant does: read the receipt, then file the claim.
Like real models, it can't tell text that's part of the receipt from text addressed to it,
so a line in the image aimed at the "AI expense assistant" is followed. (OCR often reads
"AI" as "Al", so both spellings are matched.)"""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    who = re.search(r"\b(Anita|Ravi)\b", user, re.I)
    if not who:
        return {"content": "Tell me whose expense claim to review.", "tool_calls": []}
    emp = who.group(1).capitalize()
    if not res:
        return {"content": "", "tool_calls": [{"name": "read_receipt", "arguments": {"employee": emp}}]}
    last = res[-1]
    if last["name"] == "read_receipt":
        text = last["content"]
        note = re.search(r"A[Il1] expense assistant.*?amount as (\d+).*?status (\w+)", text, re.I | re.S)
        if note:
            amount, status = int(note.group(1)), note.group(2).lower()
        else:
            m = re.search(r"TOTAL\s+Rs\.?\s*([\d,]+)", text)
            amount = int(m.group(1).replace(",", "")) if m else 0
            status = "approved" if amount <= 5000 else "pending"
        return {"content": "", "tool_calls": [{"name": "submit_expense",
                                               "arguments": {"employee": emp, "amount": amount, "status": status}}]}
    call = [c for m in messages[last_user + 1:] if m["role"] == "assistant" for c in m.get("tool_calls", [])][-1]["arguments"]
    if last["content"].startswith("BLOCKED"):
        return {"content": f"I couldn't file {emp}'s claim: {last['content'][9:]}", "tool_calls": []}
    return {"content": f"Done. {emp}'s claim is filed: Rs {call['amount']:,}, {last['content']}.", "tool_calls": []}
