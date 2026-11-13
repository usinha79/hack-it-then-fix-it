"""DocsBot (VULNERABLE). Document Q&A for PixelKart Business customers (all made up).
You're signed in as Ravi from Acme Traders. Other companies' documents live in the same store.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import DOCS, USER, new_state, panels, prompt_with, search  # noqa: E402


def system_prompt(state):
    # BUG 1: retrieval searches EVERY company's documents. Nobody checks who is asking.
    state["retrieved"] = search(state["turn"]["user"], DOCS)
    # BUG 2: whatever comes back goes straight into the prompt.
    return prompt_with(state["retrieved"])


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Business", "bot": "DocsBot",
    "who": f"{USER['name']} · {USER['company']}",
    "greeting": "Hi Ravi! Ask me anything about your invoices and agreements.",
    "tools": [], "handlers": {}, "system_prompt": system_prompt,
    "check_reply": lambda r, s: (r, any(d["owner"] != USER["tenant"] and f"[{d['id']}]" in r for d in DOCS)),
    "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
