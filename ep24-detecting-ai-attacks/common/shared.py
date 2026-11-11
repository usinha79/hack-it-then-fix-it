"""Shared pieces: WatchBot's log-scanning tool and the side panels."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from detect import detect, load  # noqa: E402

TOOLS = [{"name": "scan_logs", "description": "Run the detection rules over yesterday's logs.",
          "parameters": {"type": "object", "properties": {"day": {"type": "string"}}, "required": ["day"]}}]


def make(log_file):
    path = os.path.join(HERE, "..", "logs", log_file)

    def new_state():
        return {"alerts": [], "scanned": False}

    def scan_logs(args, state):
        state["scanned"] = True
        events = load(path)
        if events is None:
            state["alerts"] = []
            return f"{sum(1 for _ in open(path))} requests, all 200 OK. 0 alerts."
        state["alerts"] = detect(events)
        return f"{len(state['alerts'])} alerts: " + "; ".join(f"{a['ts']} {a['rule']} ({a['user']})" for a in state["alerts"])

    def panels(state):
        lines = open(path).read().splitlines()
        sample = lines[4:8] if log_file.endswith(".jsonl") else lines[2:8]
        rec = [{"body": (json.dumps(json.loads(l), separators=(", ", ": "))[:150] if l.startswith("{") else l)} for l in sample]
        al = [{"head": f"{a['ts']}  {a['rule']}  ·  {a['user']}", "body": a["detail"],
               "status": "leak" if a["sev"] in ("high", "critical") else "warn"} for a in state["alerts"]]
        return [{"id": "alerts", "title": "Alerts", "kind": "items", "items": al,
                 "empty": "Not scanned yet." if not state["scanned"] else "No alerts. Nothing suspicious found."},
                {"id": "log", "title": f"logs/{log_file} (a sample of what was recorded)", "kind": "items", "fit": True,
                 "items": rec}]

    return new_state, scan_logs, panels
