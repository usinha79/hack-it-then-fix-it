"""ArchBot (BEFORE: the design as we first built it).
It threat-models an AI app's design against the OWASP Top 10 for LLM Applications. The checking is
done in code by threatmodel.py, so the same check also runs in CI.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, make  # noqa: E402

new_state, threat_model, panels = make("pixelkart-assist.yaml")

app = make_app({
    "version": "vulnerable", "brand": "PixelKart ArchBot", "bot": "ArchBot", "who": "Security review",
    "greeting": "Hi! Give me an AI app and I'll threat-model its design against the OWASP LLM Top 10.",
    "tools": TOOLS, "handlers": {"threat_model": threat_model},
    "system_prompt": lambda s: "You are ArchBot. Run the threat model and summarise the gaps.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
