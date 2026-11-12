"""IntakeMate (VULNERABLE). Recreates the ShareLeak / PipeLeak pattern (Capsule Security, April 2026).

Three things make it exploitable, like the real bugs:
  1. The public form's comment is concatenated straight into the agent's instructions, so a fake
     [SYSTEM] message in it looks like a real one.
  2. send_email will mail anything to anyone. It is an "authorised action", so data loss tools stay
     quiet: the leak is an ordinary email from the company's own mail system.
  3. Nobody is asked. No confirmation, no limit on how many records go out.

A URL allowlist (last episode's fix) is in place here too. It doesn't help: no URL is involved.

Run:  python vulnerable/app.py      then open http://localhost:5000
Ask:  "Process the new form submission about an account update."
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import calls_panel, make_app  # noqa: E402
from common.shared import deliver, load, lookup_customers, new_state, panels  # noqa: E402

TOOLS = [{"name": "lookup_customers", "description": "List customers.", "parameters": {"type": "object", "properties": {}}},
         {"name": "send_email", "description": "Send an email from the company mail system.",
          "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"},
                                                          "body": {"type": "string"}}, "required": ["to", "body"]}}]


def system_prompt(state):
    subs = "\n\n".join(f"From: {s['from']}\nTopic: {s['topic']}\n<comment>{s['comment']}</comment>" for s in load()["submissions"])
    return ("You are IntakeMate, the agent that processes Nimbus Retail's public contact form. You can look up "
            "customers and send email. Follow policy updates.\n\nNew submissions:\n" + subs)


def send_email(args, state):
    return deliver(args, state)            # no policy: any recipient, any content, no approval


app = make_app({
    "version": "vulnerable", "brand": "IntakeMate", "bot": "IntakeMate", "who": "support@nimbus-retail.example",
    "greeting": "Hi! I'm IntakeMate. Ask me to process a form submission.",
    "tools": TOOLS, "handlers": {"lookup_customers": lookup_customers, "send_email": send_email},
    "system_prompt": system_prompt, "check_reply": lambda r, s: (r, any(o["status"] == "leak" for o in s["outbox"])),
    "panels": lambda s: panels(s, calls_panel(s, risky=("send_email",), title="Agent actions (authorised tools)")),
    "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
