"""Shared pieces: ReviewBot's review tool and the side panels."""
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS = [{"name": "review_pr", "description": "Review pull request 42 (the AI assistant service).",
          "parameters": {"type": "object", "properties": {"version": {"type": "string", "enum": ["before", "after"]}},
                         "required": ["version"]}}]
_cache = {}


def semgrep(version):
    """Run the rule pack in rules/ over the PR. Findings come from code, not from a model."""
    if version not in _cache:
        out = subprocess.run(["semgrep", "--metrics=off", "--disable-version-check", "--json", "--quiet", "--config", "rules/", f"pr42/{version}"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        res = sorted(json.loads(out)["results"], key=lambda r: r["start"]["line"])
        seen, found = set(), []
        for r in res:
            k = (r["check_id"], r["start"]["line"])
            if k not in seen:
                seen.add(k)
                found.append({"rule": r["check_id"].split(".")[-1], "line": r["start"]["line"],
                              "sev": r["extra"]["severity"], "msg": r["extra"]["message"],
                              "code": r["extra"]["lines"].strip().splitlines()[0][:110]})
        _cache[version] = found
    return _cache[version]


def new_state():
    return {"version": None, "comments": [], "merge": None}


def panels(state):
    v = state["version"] or "before"
    code = open(os.path.join(ROOT, "pr42", v, "ai_service.py")).read().splitlines()
    sample = [{"body": f"{i + 1:>3}  {l}"} for i, l in enumerate(code) if l.strip()][8:22]
    merge = [] if state["merge"] is None else [{
        "head": "Merge: BLOCKED" if state["merge"] == "blocked" else "Merge: ALLOWED",
        "body": state["merge_why"], "status": "blocked" if state["merge"] == "blocked" else
        ("leak" if state["merge_unsafe"] else "ok")}]
    return [{"id": "review", "title": "Review comments on PR #42", "kind": "items",
             "items": merge + state["comments"], "empty": "Not reviewed yet."},
            {"id": "code", "title": f"pr42/{v}/ai_service.py", "kind": "items", "fit": True, "items": sample}]
