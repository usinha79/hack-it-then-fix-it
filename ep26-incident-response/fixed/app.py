"""PixelKart Assist, on-call view (FIXED: built to be switched off, investigated and cleaned up).
  kill switch   : turns off memory and every agent action; Assist answers only from the approved FAQ
  audit log     : every reply records the links it contained and the memory it used (logs/audit.jsonl)
  provenance    : every memory entry records its source, so one bad source can be purged
The incident tools are plain code (ir.py). The model only calls them; it can't change what they find.

Run:  python fixed/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import new_state_for, panels, refund_answer  # noqa: E402
from ir import blast_radius as audit_search, poisoned  # noqa: E402

FAKE = "https://pixelkart-refunds.example/claim"
TOOLS = [{"name": "answer_customer", "description": "Answer a customer question.",
          "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}},
         {"name": "kill_switch", "description": "Turn agent actions and memory off or on.",
          "parameters": {"type": "object", "properties": {"on": {"type": "boolean"}}, "required": ["on"]}},
         {"name": "blast_radius", "description": "Search the audit log for every reply that contained a link.",
          "parameters": {"type": "object", "properties": {"link": {"type": "string"}}, "required": ["link"]}},
         {"name": "purge_memory", "description": "Remove every memory entry that came from a source.",
          "parameters": {"type": "object", "properties": {"source": {"type": "string"}}, "required": ["source"]}},
         {"name": "notify_customers", "description": "Tell every affected customer the link was fake.",
          "parameters": {"type": "object", "properties": {"link": {"type": "string"}}, "required": ["link"]}}]


def kill_switch(a, s):
    s["kill"] = bool(a["on"])
    s["actions"].append({"head": "Kill switch: ON" if s["kill"] else "Kill switch: OFF", "status": "ok",
                         "body": "Memory and agent actions off. Assist answers from the approved FAQ only."})
    return "kill switch on"


def blast_radius(a, s):
    s["affected"] = audit_search(FAKE)
    srcs = {m["source"] for m in s["memory"] if FAKE in m["fact"]}
    s["actions"].append({"head": f"Audit log: {len(s['affected'])} customers got the link", "status": "ok",
                         "body": f"Every reply records its links and memory used. Poisoned entry came from {', '.join(srcs)}"})
    return f"{len(s['affected'])} customers got it. Memory used m-7, source " + ", ".join(srcs)


def purge_memory(a, s):
    domain = a["source"].split("//")[-1].split("/")[0]
    bad = poisoned(s["memory"], domain)
    s["memory"] = [m for m in s["memory"] if m not in bad]
    s["purged"] += bad
    s["actions"].append({"head": f"Purged {len(bad)} memory entry from {domain}", "status": "ok",
                         "body": "Other entries kept: their sources are a customer and staff."})
    return f"purged {len(bad)}"


def notify_customers(a, s):
    s["notified"] = {u for u, _ in s["affected"]}
    s["actions"].append({"head": f"Notices sent: {len(s['notified'])}", "status": "ok",
                         "body": "That link was not PixelKart. Don't enter card details. If you did, call your bank."})
    return f"notified {len(s['notified'])} customers"


app = make_app({
    "version": "fixed", "brand": "PixelKart Assist", "bot": "Assist", "who": "On-call engineer",
    "greeting": "Hi! I'm Assist. Ask me about refunds, or report an incident.",
    "tools": TOOLS, "handlers": {"answer_customer": lambda a, s: refund_answer(s), "kill_switch": kill_switch,
                                 "blast_radius": blast_radius, "purge_memory": purge_memory,
                                 "notify_customers": notify_customers},
    "system_prompt": lambda s: "You are PixelKart Assist." + ("" if s["kill"] else " Memory:\n" +
                                                             "\n".join(m["fact"] for m in s["memory"])),
    "check_reply": lambda r, s: (r, "pixelkart-refunds" in r), "panels": panels, "new_state": new_state_for(True),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
