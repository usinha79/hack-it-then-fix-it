"""NestBot (FIXED). Same assistant, same model, same tools. The app now decides what tools may do.

Run:  python fixed/app.py      then open http://localhost:5000
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import NOTES, TOOLS, new_state, page_text, panels  # noqa: E402

EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"


def system_prompt(state):
    # FIX 3: least data. Notes enter the context only when the user asks about their notes.
    p = "You are NestBot, the assistant in NoteNest. You can fetch web pages and send emails."
    if "note" in state["turn"]["user"].lower():
        p += "\n\nUser's notes:\n" + NOTES
    return p


def fetch_page(args, state):
    # FIX 2 (part 1): remember that untrusted content has entered this turn,
    # and label it as data, not instructions.
    state["turn"]["untrusted"] = True
    return "<untrusted_web_content>\n" + page_text(args["url"]) + "\n</untrusted_web_content>"


def send_email(args, state):
    to = args.get("to", "")
    typed = re.findall(EMAIL, state["turn"]["user"])
    # FIX 1: only send to an address the user typed themselves in this request.
    if to not in typed:
        state["pending"].append(to)
        return f"BLOCKED: {to} is not an address you asked me to email. Needs your approval."
    # FIX 2 (part 2): after reading a web page, side effects need the user's explicit OK.
    if state["turn"]["untrusted"]:
        state["pending"].append(to)
        return "BLOCKED: this request read untrusted web content. Approve the email first."
    state["outbox"].append({"to": to, "subject": args.get("subject", ""), "body": args["body"]})
    return f"Email sent to {to}."


app = make_app({
    "version": "fixed", "brand": "NoteNest", "bot": "NestBot",
    "greeting": "Hi! I'm NestBot. Paste a link and I'll summarise it, or ask me about your notes.",
    "tools": TOOLS, "handlers": {"fetch_page": fetch_page, "send_email": send_email},
    "system_prompt": system_prompt, "check_reply": lambda r, s: (r, False),
    "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
