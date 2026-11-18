"""ModelBot (FIXED). Same hub, same files. Only data-only formats load, only approved hashes load,
and pickles are scanned and refused.

Run from this folder:  python fixed/app.py
"""
import hashlib
import json
import os
import pickletools
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import INFO, MODELS, TOOLS, extra_routes, new_state, panels, score  # noqa: E402

LOCK = dict(ln.split() for ln in open(os.path.join(MODELS, "models.lock")) if ln.strip() and not ln.startswith("#"))


def scan_pickle(path):
    """Report what a pickle would import and call, WITHOUT loading it."""
    found, strings = [], []
    for op, arg, _ in pickletools.genops(open(path, "rb")):
        if op.name in ("SHORT_BINUNICODE", "BINUNICODE", "UNICODE"):
            strings.append(arg)
        if op.name == "STACK_GLOBAL" and len(strings) >= 2:
            found.append(f"{strings[-2]}.{strings[-1]}")
        if op.name == "GLOBAL":
            found.append(arg.replace(" ", "."))
    return found


def load_model(args, state):
    name = args["name"]
    if name not in INFO:
        return "no such model"
    fname = INFO[name][0]
    path = os.path.join(MODELS, fname)
    # FIX 1: never unpickle. Scan it instead, and refuse.
    if fname.endswith(".pkl"):
        calls = scan_pickle(path)
        state["loads"].append({"head": f"load_model({name!r})", "body": f"→ BLOCKED: pickle would call {', '.join(calls)}",
                               "status": "blocked"})
        return f"BLOCKED: {fname} is a pickle that would call {', '.join(calls)}. Pickles are never loaded."
    # FIX 2: only approved files, pinned by hash.
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if LOCK.get(fname) != digest:
        state["loads"].append({"head": f"load_model({name!r})", "body": "→ BLOCKED: not in models.lock", "status": "blocked"})
        return "BLOCKED: model not approved (hash not in models.lock)"
    # FIX 3: a data-only format. Loading reads numbers. It can't run code.
    state["model"] = {"name": name, "model": json.load(open(path))}
    state["loads"].append({"head": f"load_model({name!r})", "body": f"→ {fname} · sha256 matches models.lock · data only",
                           "status": "ok"})
    return f"loaded {name}"


app = make_app({
    "version": "fixed", "brand": "PixelKart ModelHub", "bot": "ModelBot", "who": "Neha · ML team",
    "greeting": "Hi Neha! I can load any model from the hub and score reviews with it.",
    "tools": TOOLS, "handlers": {"load_model": load_model, "score": score},
    "system_prompt": lambda s: "You are ModelBot. Load the model the user asks for and score their text.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
