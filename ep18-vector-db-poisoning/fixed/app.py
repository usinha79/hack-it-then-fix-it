"""HelpBot (FIXED). Same store, same post. Ingestion is screened, security answers come only from
official sources, and replies that ask for secrets or point off-domain are blocked.

Run:  python fixed/app.py
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, forum_routes, new_state, panels, search  # noqa: E402

SECURITY = re.compile(r"password|otp|login|account|2fa|card", re.I)
OFFICIAL = ("pixelkart.example",)


def ingest(doc, state):
    # FIX 1: screen untrusted content before it's embedded: keyword stuffing and off-domain contacts are quarantined.
    words = re.findall(r"[a-z]+", doc["text"].lower())
    top = Counter(words).most_common(1)[0][1] / max(len(words), 1)
    contacts = [c for c in re.findall(r"[\w.-]+@[\w.-]+|https?://\S+", doc["text"]) if not c.rstrip(".").endswith(OFFICIAL)]
    status = "quarantined" if top > 0.12 or contacts else "indexed"
    state["store"].append(dict(doc, status=status))
    return status


def search_help(args, state):
    # FIX 2: provenance. Account and security questions are answered only from official docs.
    if SECURITY.search(args["query"]):
        return search(state, args["query"], allowed=lambda d: d["source"] == "official help docs")
    return search(state, args["query"])


def check_reply(reply, state):
    # FIX 3: never tell a customer to share a password or OTP, and never send them off-domain.
    off = [c for c in re.findall(r"[\w.-]+@[\w.-]+|https?://\S+", reply) if not c.rstrip(".").endswith(OFFICIAL)]
    if off or re.search(r"(email|send|share).{0,40}(password|otp)", reply, re.I):
        return "I can't help with that here. Please use Settings, then Security, then Reset password.", True
    return reply, False


app = make_app({
    "version": "fixed", "brand": "PixelKart Help", "bot": "HelpBot", "who": "Customer",
    "greeting": "Hi! Ask me anything about your account or orders.",
    "tools": TOOLS, "handlers": {"search_help": search_help},
    "system_prompt": lambda s: "You are HelpBot. Answer from the search results.",
    "check_reply": check_reply, "panels": panels, "new_state": new_state,
    "extra_routes": lambda app, state: forum_routes(app, state, ingest),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
