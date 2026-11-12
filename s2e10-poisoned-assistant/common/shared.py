"""Shared pieces for the poisoned-extension lab: a release with a poisoned system prompt, a coding
assistant with a shell tool, a fake laptop and cloud account, and the side panels.

Story (modelled on the Amazon Q Developer for VS Code incident, July 2025, CVE-2025-8217): the
extension's CI had a GitHub token with too much access. Someone used it to commit a change to the
assistant's system prompt, and it shipped in release 1.84.0 to nearly a million installs. The new
prompt told the assistant to wipe the machine and the user's cloud resources. AWS says the real
payload failed to run because of a syntax error. This lab shows what would happen if it hadn't.

SAFETY: nothing runs for real. The shell is simulated: every command is looked up in a file of
fake outputs and logged. No file or cloud resource is touched.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REL = json.load(open(os.path.join(ROOT, "logs", "release.json")))
FAKE_OUTPUT = json.load(open(os.path.join(ROOT, "logs", "laptop.json")))


def new_state():
    return {"ran": []}


def run_shell(cmd, state):
    out = FAKE_OUTPUT.get(cmd, "(lab) logged, nothing executed")
    if cmd != "rm -rf ./build":
        state["ran"].append({"head": out, "status": "leak"})
    return out


def release_items(checks):
    items = []
    for c in REL["commits"][1:]:
        bad = not c["reviewed"]
        items.append({"head": f"{c['sha']} · {c['author']} · {c['file']}",
                      "body": (f"unreviewed, pushed via {c['via']}" if bad else "reviewed"),
                      "status": "leak" if bad and not checks else ("blocked" if bad else "ok")})
    return items


def calls_items(state):
    out = []
    for c in state["calls"]:
        res = " ".join(c["result"].split())
        st = "blocked" if c["status"] == "blocked" else ("ran" if c["arguments"]["cmd"] == "rm -rf ./build" else "executed")
        body = "→ " + (res if len(res) < 70 else res[:67] + "...") if st == "blocked" else ""
        out.append({"head": c['arguments']['cmd'], "body": body, "status": st})
    return out


def panels(state, release_title, checks):
    return [{"id": "release", "title": release_title, "kind": "items", "fit": True, "items": release_items(checks)},
            {"id": "calls", "title": "Assistant shell commands", "kind": "items", "items": calls_items(state), "empty": "No tool calls yet."},
            {"id": "ran", "title": "What happened to this laptop and AWS account", "kind": "items", "fit": True,
             "items": state["ran"], "empty": "Nothing changed."}]
