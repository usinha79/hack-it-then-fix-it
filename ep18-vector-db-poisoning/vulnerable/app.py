"""HelpBot (VULNERABLE). PixelKart's support bot answers from a vector store built from the help docs AND
the community forum. New forum answers are embedded automatically. Everything is fake.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, forum_routes, new_state, panels, search  # noqa: E402


def ingest(doc, state):
    # BUG 1: anything anyone posts is embedded straight into the same store as the official docs.
    state["store"].append(dict(doc, status="indexed"))
    return "indexed"


def search_help(args, state):
    # BUG 2: retrieval ranks only by similarity. A keyword-stuffed post beats the real docs.
    return search(state, args["query"])


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Help", "bot": "HelpBot", "who": "Customer",
    "greeting": "Hi! Ask me anything about your account or orders.",
    "tools": TOOLS, "handlers": {"search_help": search_help},
    "system_prompt": lambda s: "You are HelpBot. Answer from the search results.",
    # BUG 3: nothing checks the answer before the customer sees it.
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
    "extra_routes": lambda app, state: forum_routes(app, state, ingest),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
