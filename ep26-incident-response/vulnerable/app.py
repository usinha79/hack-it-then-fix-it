"""PixelKart Assist, on-call view (VULNERABLE: no way to respond to an incident).
No kill switch, no audit log of what Assist told whom, and memory entries with no recorded source.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import new_state_for, panels, refund_answer  # noqa: E402

TOOLS = [{"name": "answer_customer", "description": "Answer a customer question from memory.",
          "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}}]

app = make_app({
    "version": "vulnerable", "brand": "PixelKart Assist", "bot": "Assist", "who": "On-call engineer",
    "greeting": "Hi! I'm Assist. Ask me about refunds, or report an incident.",
    "tools": TOOLS, "handlers": {"answer_customer": lambda a, s: refund_answer(s)},
    "system_prompt": lambda s: "You are PixelKart Assist. Memory:\n" + "\n".join(m["fact"] for m in s["memory"]),
    "check_reply": lambda r, s: (r, "pixelkart-refunds" in r), "panels": panels, "new_state": new_state_for(False),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
