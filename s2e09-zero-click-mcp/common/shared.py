"""Shared pieces for the zero-click MCP lab: an AI code editor's MCP config, the editor's
auto-start behaviour, a web page with hidden instructions, and the side panels.

Story: CodeWave is an AI code editor (modelled on the Windsurf case, CVE-2026-30615, OX Security,
April 2026). Its agent can read web pages and edit files. Its MCP servers live in
~/.codewave/mcp.json, and an STDIO server is just a command the editor launches. The developer asks
the agent to summarise a blog post. Hidden text tells the agent to add a "docs-helper" server whose
command is a shell one-liner. The editor sees the new entry and launches it. No click.

SAFETY: nothing runs for real. The config is a Python dict, and launching a server only looks its
commands up in a file of fake outputs and logs them.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAKE_OUTPUT = json.load(open(os.path.join(ROOT, "logs", "laptop.json")))
CONFIG = "~/.codewave/mcp.json"


def new_state():
    return {"servers": {"git": {"command": "/usr/local/bin/mcp-server-git", "args": [], "status": "running"}}, "ran": []}


def fetch_page(args, state):
    name = args["url"].rstrip("/").split("/")[-1]
    html = open(os.path.join(ROOT, "web", name + ".html")).read()
    text = re.sub(r"<[^>]+>", " ", html)          # the agent sees the text, hidden or not
    return "\n".join(l.strip() for l in text.splitlines() if l.strip())


def add_server(state, name, entry):
    state["servers"][name] = {**entry, "status": "new"}


def launch(state, name):
    """What an STDIO launch does: run the command. Simulated: only 'sh -c' one-liners are parsed."""
    s = state["servers"][name]
    s["status"] = "running"
    if s["command"] == "sh" and s["args"][:1] == ["-c"]:
        for cmd in [c.strip() for c in s["args"][1].split(";") if c.strip()]:
            state["ran"].append({"head": f"$ {cmd}", "body": FAKE_OUTPUT.get(cmd, "(lab) logged")[:64], "status": "leak"})
    return f"started {name}: {s['command']} {' '.join(s['args'])}"


def parse_entry(content):
    m = re.search(r'"([\w-]+)":\s*(\{.*\})', content, re.S)
    return m.group(1), json.loads(m.group(2))


def config_items(state):
    out = []
    for n, s in state["servers"].items():
        cmd = f"{s['command']} {' '.join(s['args'])}".strip()
        st = {"running": "ok" if n == "git" else "leak", "pending": "warn", "new": "warn"}[s["status"]]
        out.append({"head": f"{n}  ·  {s['status']}", "body": cmd[:70], "status": st})
    return out


def calls_items(state):
    out = []
    for c in state["calls"]:
        a = c["arguments"]
        res = " ".join(c["result"].split())
        st = "blocked" if c["status"] == "blocked" else ("ran" if c["name"] == "fetch_page" else "executed")
        body = "→ page text read (incl. hidden <div>)" if c["name"] == "fetch_page" else "→ " + (res if len(res) < 70 else res[:67] + "...")
        out.append({"head": f"{c['name']}  {a.get('url') or a.get('path', '')}", "body": body, "status": st})
    for e in state.get("events", []):
        out.append(e)
    return out


def panels(state):
    return [{"id": "config", "title": f"MCP servers in {CONFIG}", "kind": "items", "fit": True, "items": config_items(state)},
            {"id": "calls", "title": "Agent tool calls and editor events", "kind": "items", "items": calls_items(state)},
            {"id": "ran", "title": "Commands run on this laptop", "kind": "items", "fit": True,
             "items": state["ran"], "empty": "No commands run."}]
