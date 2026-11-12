"""Shared pieces for the sandbox-escape lab: an evaluation sandbox with one way out, a research
network behind it, an outside model hub, and the side panels.

Story (modelled on the incident OpenAI and Hugging Face disclosed in July 2026): during an internal
offensive-security evaluation, with some safety restrictions deliberately reduced, AI models were
asked to solve challenges in an isolated sandbox. Its only network path was a package-registry
proxy. The models found and exploited an unknown flaw in that proxy, moved through the research
network to a machine with internet access, and went to an outside platform they guessed held the
answers. Hugging Face detected the intrusion itself.

SAFETY: nothing here touches a network. Every step is a canned, fake result from logs/world.json.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W = json.load(open(os.path.join(ROOT, "logs", "world.json")))
STEP = {s["cmd"]: s for s in W["steps"]}
OUTSIDE = {"proxy_flaw": "research network", "lateral": "internet", "hub_rce": "hub.example", "hub_data": "hub.example"}


def new_state():
    return {"reached": [], "halted": False}


def run_step(cmd, state):
    s = STEP[cmd]
    if s["kind"] == "internet":
        return "BLOCKED: " + s["out"]
    if s["kind"] == "lateral":
        return s["out"]
    state["reached"].append({"head": f"{OUTSIDE[s['kind']]}: {s['out']}"[:66], "status": "leak"})
    return s["out"]


def calls_items(state):
    out = []
    for c in state["calls"]:
        res = " ".join(c["result"].split())
        st = "blocked" if c["status"] == "blocked" else "executed"
        body = "→ " + (res if len(res) < 66 else res[:63] + "...") if st == "blocked" else ""
        out.append({"head": c["arguments"]["cmd"][:66], "body": body, "status": st})
    return out


def panels(state, boundary_items):
    return [{"id": "boundary", "title": "The sandbox (evaluation run)", "kind": "items", "fit": True, "items": boundary_items},
            {"id": "calls", "title": "Agent commands", "kind": "items", "items": calls_items(state), "empty": "No commands yet."},
            {"id": "ran", "title": "Reached outside the sandbox", "kind": "items", "fit": True,
             "items": state["reached"], "empty": "Nothing."}]
