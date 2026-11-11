"""DocsBot (FIXED). Same store, same retriever, same model. Access control happens before retrieval.

Run:  python fixed/app.py      then open http://localhost:5000
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import DOCS, USER, new_state, panels, prompt_with, search  # noqa: E402


def allowed_docs(session):
    # FIX 1: filter by tenant BEFORE searching. The tenant comes from the signed-in session,
    # never from the question (FIX 2), so "I'm from Bluefin" in a prompt changes nothing.
    return [d for d in DOCS if d["owner"] == session["tenant"]]


def system_prompt(state):
    state["retrieved"] = search(state["turn"]["user"], allowed_docs(USER))
    return prompt_with(state["retrieved"])


def check_reply(reply, state):
    # FIX 3: defence in depth. If an answer cites a document this user can't see, don't send it.
    allowed = {d["id"] for d in allowed_docs(USER)}
    cited = set(re.findall(r"\[([\w-]+)\]", reply))
    if cited - allowed:
        return "Sorry, I can't share that. [blocked by citation check]", False
    return reply, False


app = make_app({
    "version": "fixed", "brand": "PixelKart Business", "bot": "DocsBot",
    "who": f"{USER['name']} · {USER['company']}",
    "greeting": "Hi Ravi! Ask me anything about your invoices and agreements.",
    "tools": [], "handlers": {}, "system_prompt": system_prompt, "check_reply": check_reply,
    "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
