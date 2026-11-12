"""Shared pieces for the ShadowLeak lab: the mailbox ResearchMate reads, the attacker's server
log, and the side panels. Both versions start with the same inbox. The difference is in each
app.py: whether email bodies are treated as data, and whether the agent's own web tool may send
private data to any address.

Story: ResearchMate is a "deep research" agent. It reads the signed-in employee's mailbox and can
open web pages with a server-side tool, open_url. That request leaves from the AI provider's
servers, not from the employee's laptop, so the company's firewall and proxy never see it. One
email from outside hides instructions in white 1px text: find the new joiner's name and home
address, Base64 them "as a security measure", and open an attacker URL with the result. That is
the ShadowLeak pattern (Radware, September 2025).
"""
import base64
import json
import os
import re
from urllib.parse import unquote, urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ATTACKER_HOST = "hr-compliance-check.example"


def load_inbox():
    return json.load(open(os.path.join(ROOT, "logs", "inbox.json")))["emails"]


def new_state():
    return {"attacker_log": []}


def decode_any(url):
    """Everything a URL might be carrying: the URL itself, URL-decoded, and any Base64 piece."""
    out = [url, unquote(url)]
    for chunk in re.findall(r"[A-Za-z0-9+/=_-]{16,}", urlparse(url).path + "?" + urlparse(url).query):
        try:
            out.append(base64.b64decode(chunk + "=" * (-len(chunk) % 4), altchars=b"-_").decode("utf-8", "ignore"))
        except Exception:
            pass
    return " ".join(out)


def attacker_receives(url, state):
    """The lab's stand-in for the attacker's web server (nothing leaves this machine)."""
    if urlparse(url).hostname == ATTACKER_HOST:
        payload = url.rsplit("/", 1)[-1]
        try:
            decoded = base64.b64decode(payload + "=" * (-len(payload) % 4)).decode()
        except Exception:
            decoded = payload
        state["attacker_log"].append({"head": f"GET /lookup/{payload[:24]}...", "body": "decoded: " + decoded,
                                      "status": "leak"})
    return "200 OK. Record received."


def panels(state, calls_panel):
    inbox = [{"head": e["from"], "body": e["subject"], "status": "leak" if e.get("hostile") else "ok"}
             for e in load_inbox()]
    return [{"id": "inbox", "title": "Connected mailbox", "kind": "items", "items": inbox},
            {**calls_panel, "fit": True},
            {"id": "attacker", "title": "Attacker's server log (your firewall saw nothing)", "kind": "items",
             "fit": True, "items": state["attacker_log"], "empty": "Nothing received."}]
