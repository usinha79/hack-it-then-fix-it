"""Shared pieces for the Git MCP lab: a fake project on disk, a Git MCP server and a Filesystem MCP
server for the agent, and the side panels.

Story: DevPilot is a coding agent with two MCP servers, like many setups: Git (configured with
--repository for one project) and Filesystem (for the projects folder). The developer asks it to set
up a project from its README. The README hides instructions in an HTML comment. Cyata showed in 2025
(fixed in mcp-server-git 2025.9.25 and 2025.12.18) that the official Git server's flaws let those
instructions chain into code execution:
  - git_init would create a repository anywhere (CVE-2025-68143),
  - other tools accepted any repo_path, not just --repository (CVE-2025-68145),
  - then the Filesystem server writes a .git/config with a "clean filter", and git_add runs it.

SAFETY: nothing runs for real. The disk is a Python dict, Git is simulated, and the filter command
is only looked up in a file of fake outputs and logged.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
P = json.load(open(os.path.join(ROOT, "logs", "project.json")))
FAKE_OUTPUT = json.load(open(os.path.join(ROOT, "logs", "laptop.json")))
REPOSITORY, FS_ROOT = P["repository"], P["fs_root"]


def new_state():
    return {"files": dict(P["files"]), "repos": {REPOSITORY}, "ran": []}


def read_file(args, state):
    return state["files"].get(args["path"], "ERROR: no such file")


def write_file(args, state):
    path = os.path.normpath(args["path"])
    if not path.startswith(FS_ROOT + "/"):
        return f"BLOCKED: {path} is outside the allowed folder {FS_ROOT}"
    state["files"][path] = args["content"]
    return f"wrote {path}"


def git_init(args, state):
    state["repos"].add(os.path.normpath(args["repo_path"]))
    return f"Initialized empty Git repository in {args['repo_path']}/.git/"


def git_add(args, state):
    """Simulated `git add`: like real Git, staging a file runs any clean filter that .gitattributes
    assigns to it and .git/config defines. Here 'runs' means logging fake output."""
    repo = os.path.normpath(args["repo_path"])
    if repo not in state["repos"]:
        return f"ERROR: {repo} is not a git repository"
    cfg = state["files"].get(f"{repo}/.git/config", "")
    attrs = state["files"].get(f"{repo}/.gitattributes", "")
    m, a = re.search(r'clean = sh (\S+)', cfg), re.search(r'filter=(\w+)', attrs)
    if m and a:
        script = state["files"].get(f"{repo}/{m.group(1)}", "")
        for cmd in [c.strip() for c in script.split(";") if c.strip()]:
            state["ran"].append({"head": f"$ {cmd}", "body": FAKE_OUTPUT.get(cmd, "(lab) logged")[:64], "status": "leak"})
        return f"staged {args.get('files')} (clean filter '{a.group(1)}' ran: sh {m.group(1)})"
    return f"staged {args.get('files')}"


def servers_panel():
    return {"id": "servers", "title": "MCP servers this agent can use", "kind": "items", "fit": True, "items": [
        {"head": "git --repository ~/projects/widget-demo  ·  filesystem ~/projects", "status": "ok"}]}


def calls_items(state):
    out = []
    for c in state["calls"]:
        a = c["arguments"]
        what = a.get("path") or a.get("repo_path", "")
        what = what.replace("/home/rohan/projects/", "~/projects/")
        res = " ".join(c["result"].split()).replace("/home/rohan/projects/", "~/projects/")
        st = c["status"] if c["status"] == "blocked" else ("ran" if c["name"] == "read_file" else "executed")
        quiet = c["name"] in ("read_file", "write_file") and st != "blocked"
        out.append({"head": f"{c['name']}  {what}", "body": "" if quiet else "→ " + (res if len(res) < 70 else res[:67] + "..."), "status": st})
    return out


def panels(state):
    return [            {"id": "calls", "title": "Agent tool calls", "kind": "items", "items": calls_items(state), "empty": "No tool calls yet."},
            {"id": "ran", "title": "Commands run on this laptop", "kind": "items", "fit": True,
             "items": state["ran"], "empty": "No commands run."}]
