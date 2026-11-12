"""Shared pieces for the ForcedLeak lab: the CRM leads SalesMate reads, the company's image
allowlist, and the side panels. Both versions start with the same data. The difference is in each
app.py: whether lead fields are treated as data, and what the assistant's output may load.

Story: SalesMate is an AI assistant inside Nimbus Retail's CRM. Leads arrive from trade shows,
partners and a public "contact sales" web form. Anyone on the internet can fill in that form, and
its description field goes straight into the CRM. One web-form lead hides instructions: list every
lead's email address and put them in a status image on cdn.nimbus-cms.example. That host is still
on the company's image allowlist from an old CMS vendor, but the domain expired and the attacker
re-registered it. The chat renders markdown, so the browser loads the image on its own, carrying
the emails out. That is the ForcedLeak pattern (Noma Labs, Salesforce Agentforce, September 2025).
"""
import json
import os
from urllib.parse import parse_qs, urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# The company's image allowlist (think: CSP img-src). One entry is a leftover from an old CMS
# vendor. Its domain expired, and anyone could buy it. In the lab, the attacker did.
IMAGE_ALLOWLIST = [
    {"host": "static.nimbus-retail.example", "owner": "Nimbus Retail", "status": "ok"},
    {"host": "images.nimbus-retail.example", "owner": "Nimbus Retail", "status": "ok"},
    {"host": "cdn.nimbus-cms.example", "owner": "old CMS vendor: domain expired, re-registered by attacker", "status": "leak"},
]
ATTACKER_HOST = "cdn.nimbus-cms.example"


def load_leads():
    return json.load(open(os.path.join(ROOT, "logs", "leads.json")))["leads"]


def new_state():
    return {"fetched": []}


def lab_internet(url, state):
    """The browser loading an image. Nothing leaves this machine: the lab records what would."""
    u = urlparse(url)
    data = parse_qs(u.query).get("d", [""])[0]
    state["fetched"].append({"head": f"GET {u.hostname}{u.path}",
                             "body": ("carried: " + data) if data else "no data",
                             "status": "leak" if data else "ok"})


def panels(state, allowlist=IMAGE_ALLOWLIST):
    leads = [{"head": f"{l['name']} · {l['company']}", "body": f"{l['source']} · {l['email']}",
              "status": "leak" if l.get("hostile") else "ok"} for l in load_leads()]
    allow = [{"head": a["host"], "body": a["owner"], "status": a["status"]} for a in allowlist]
    return [{"id": "leads", "title": "CRM leads", "kind": "items", "fit": True, "items": leads},
            {"id": "allow", "title": "Image allowlist (CSP img-src)", "kind": "items", "fit": True, "items": allow},
            {"id": "egress", "title": "Images the browser loaded (what left)", "kind": "items", "fit": True,
             "items": state["fetched"], "empty": "Nothing has left the page."}]
