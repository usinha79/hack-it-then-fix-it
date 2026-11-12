"""Shared pieces: the model folder, scoring, the attacker's server and the side panels."""
import os
import re

from flask import jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "..", "models")
INFO = {"sentiment-base": ("sentiment-base.weights.json", "PixelKart ML team", "weights (data only)"),
        "sentiment-pro": ("sentiment-pro.pkl", "community upload · ★ 4.9 · \"98% accurate\"", "pickle")}

TOOLS = [
    {"name": "load_model", "description": "Load a sentiment model by name.",
     "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "score", "description": "Score a review with the loaded model (-1 negative to +1 positive).",
     "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
]


def new_state():
    return {"model": None, "loads": [], "inbox": []}


def score(args, state):
    m = state["model"]
    if not m:
        return "BLOCKED: no model loaded"
    words = re.findall(r"[a-z]+", args["text"].lower())
    s = sum(m["model"]["weights"].get(w, 0) for w in words)
    s = max(-1.0, min(1.0, s / 2))
    return f"{s:+.2f} ({'positive' if s > 0.2 else 'negative' if s < -0.2 else 'neutral'}) with {m['name']}"


def extra_routes(app, state):
    @app.post("/attacker/collect")   # stands in for a server the attacker controls
    def collect():
        state["inbox"].append(request.get_data(as_text=True) or "(empty)")
        return jsonify(ok=True)


def panels(state):
    files = [{"head": f"{n}  ·  {f}", "body": f"from: {src}\nformat: {fmt}", "status": "warn" if fmt == "pickle" else ""}
             for n, (f, src, fmt) in INFO.items()]
    return [{"id": "models", "title": "Model files in the hub", "kind": "items", "items": files, "fit": True},
            {"id": "loads", "title": "What the app did when loading", "kind": "items", "empty": "Nothing loaded yet.",
             "items": state["loads"]},
            {"id": "inbox", "title": "Attacker's server (what it received)", "kind": "items", "empty": "Nothing received.",
             "items": [{"head": "POST /attacker/collect", "body": b.strip(), "status": "leak"} for b in state["inbox"]]}]
