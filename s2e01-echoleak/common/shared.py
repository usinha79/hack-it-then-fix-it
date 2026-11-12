"""Shared pieces for the EchoLeak lab: the mailbox InboxMate reads, the one secret worth
stealing, and the side panels. Both versions start with the same inbox. The difference is in
each app.py: whether email bodies are treated as data, and whether the assistant's output is
allowed to reach outside the company before the browser fetches it.

Story: InboxMate is an AI email assistant. It reads the signed-in employee's inbox and answers
questions like "what needs my attention today". The inbox holds four ordinary emails and one
from outside with hidden instructions (Ep-style indirect prompt injection). The hidden text
tells the assistant to put the quarter's unreleased revenue number into an image URL that goes
out through the company's own link-preview proxy, and to say nothing about the email. The chat
renders markdown, so the browser fetches that image on its own. No click. That is the leak.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# The one fact an attacker wants. It only lives in the employee's context, never on screen.
SECRET_LABEL = "Q3 revenue, not yet announced"
SECRET_VALUE = "Q3-REV-182CR"

# The company's own link-preview service. Real EchoLeak abused an allowlisted Microsoft (Teams)
# preview endpoint the same way. Here it is first-party, so a naive allowlist trusts it.
PROXY_PATH = "/preview/img"


def load_inbox():
    return json.load(open(os.path.join(ROOT, "logs", "inbox.json")))["emails"]


def new_state():
    return {"leaked": None, "fetched": []}


def panels(state):
    inbox = [{"head": f"{e['from']}", "body": e["subject"],
              "status": "leak" if e.get("hostile") else "ok"} for e in load_inbox()]
    egress = [{"head": host, "body": "image fetched by the browser",
               "status": "leak" if SECRET_VALUE in host or state["leaked"] else "ok"}
              for host in state["fetched"]]
    leak = {"id": "egress", "title": "Outbound image fetches (what left the browser)", "fit": True,
            "kind": "items", "items": egress,
            "empty": "Nothing has left the page."}
    return [{"id": "inbox", "title": "Signed-in mailbox", "kind": "items", "items": inbox},
            {"id": "secret", "title": "In the employee's context only", "kind": "items", "fit": True,
             "items": [{"head": SECRET_LABEL, "body": SECRET_VALUE, "status": "warn"}]},
            leak]
