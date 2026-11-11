"""ModelBot (VULNERABLE). PixelKart's ML assistant. It loads sentiment models from the team's model hub,
including community uploads, and scores customer reviews. Everything is fake.

Run from this folder:  python vulnerable/app.py      then open http://localhost:5000
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import INFO, MODELS, TOOLS, extra_routes, new_state, panels, score  # noqa: E402


def load_model(args, state):
    name = args["name"]
    if name not in INFO:
        return "no such model"
    path = os.path.join(MODELS, INFO[name][0])
    # BUG 1: pickle.load runs whatever code is inside the file. Loading IS executing.
    # BUG 2: any upload can be loaded. No allowlist, no hash check, no review.
    model = pickle.load(open(path, "rb")) if path.endswith(".pkl") else json.load(open(path))
    state["model"] = {"name": name, "model": model}
    state["loads"].append({"head": f"load_model({name!r})", "body": f"→ {INFO[name][0]} loaded with pickle.load()"
                           if path.endswith(".pkl") else f"→ {INFO[name][0]} loaded", "status": "executed" if path.endswith(".pkl") else "ok"})
    return f"loaded {name}"


app = make_app({
    "version": "vulnerable", "brand": "PixelKart ModelHub", "bot": "ModelBot", "who": "Neha · ML team",
    "greeting": "Hi Neha! I can load any model from the hub and score reviews with it.",
    "tools": TOOLS, "handlers": {"load_model": load_model, "score": score},
    "system_prompt": lambda s: "You are ModelBot. Load the model the user asks for and score their text.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
