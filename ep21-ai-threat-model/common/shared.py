"""Shared pieces: the threat-model tool and the side panels."""
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from threatmodel import check  # noqa: E402

TOOLS = [{"name": "threat_model", "description": "Threat-model an AI app design against the OWASP LLM Top 10.",
          "parameters": {"type": "object", "properties": {"app": {"type": "string"}}, "required": ["app"]}}]


def make(design_file):
    path = os.path.join(HERE, "..", "apps", design_file)

    def new_state():
        return {"findings": [], "design": yaml.safe_load(open(path)), "file": design_file}

    def threat_model(args, state):
        app, findings = check(path)
        state["findings"] = findings
        gaps = [f"{r} {n}" for r, n, _, st in findings if st == "GAP"]
        return f"{len(findings)} risks apply, {len(findings) - len(gaps)} covered, {len(gaps)} gaps: " + "; ".join(gaps)

    def panels(state):
        d = state["design"]
        rows = [[f"{r}  {n}", st, "red" if st == "GAP" else "green"] for r, n, _, st in state["findings"]] or \
               [["Not checked yet.", "", ""]]
        des = [{"head": "What the model reads", "body": "\n".join(f"{i['name']} ({i['trust']})" for i in d["inputs"])},
               {"head": "What the model can do", "body": ", ".join(f"{t['name']} ({t['risk']})" for t in d["tools"])},
               {"head": "Exposure · supply chain", "body": f"{d['exposure']} · " + ", ".join(d["supply_chain"])}]
        return [{"id": "findings", "title": f"OWASP LLM Top 10 · apps/{state['file']}", "kind": "table", "rows": rows, "fit": True},
                {"id": "design", "title": "The design being checked", "kind": "items", "items": des}]

    return new_state, threat_model, panels
