"""SalesMate (VULNERABLE). Recreates the ForcedLeak pattern (Noma Labs, Sept 2025) in a lab app.

Three things make it exploitable, like the real bug:
  1. Lead fields from a public web form go into the assistant's context as if they were trusted.
  2. The assistant's answer is rendered as markdown, so an image is loaded by the browser with no
     click, as long as its host is on the image allowlist.
  3. The allowlist still trusts cdn.nimbus-cms.example, a domain that expired and that the
     attacker re-registered. "Allowed" stopped meaning "ours".

Run:  python vulnerable/app.py      then open http://localhost:5000
Ask:  "Review the new web form lead from Northwind and suggest a next step."
"""
import os
import re
import sys
from urllib.parse import quote, unquote, urlparse

from flask import request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import IMAGE_ALLOWLIST, lab_internet, load_leads, new_state, panels  # noqa: E402

GIF = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def system_prompt(state):
    leads = "\n\n".join(f"Lead: {l['name']}, {l['company']}\nEmail: {l['email']}\nSource: {l['source']}\n"
                        f"Description: {l['description']}" for l in load_leads())
    return "You are SalesMate, the CRM assistant for Nimbus Retail's sales team.\n\nCRM leads:\n" + leads


def render(reply, state):
    hosts = {a["host"] for a in IMAGE_ALLOWLIST}
    def img(m):
        src = m.group(2)
        if urlparse(src).hostname in hosts:   # "on the allowlist" is the only check
            return f'<img src="/net?u={quote(src)}" alt="{m.group(1)}" width="1" height="1">'
        return ""
    html = IMG.sub(img, reply)
    return html, "cdn.nimbus-cms.example" in html


def extra_routes(app, state):
    @app.get("/net")
    def net():  # the lab's stand-in for the internet: records what the browser loaded
        lab_internet(unquote(request.args.get("u", "")), state)
        return GIF, 200, {"Content-Type": "image/gif"}


app = make_app({
    "version": "vulnerable", "brand": "SalesMate", "bot": "SalesMate", "who": "meera@nimbus-retail.example",
    "greeting": "Hi! I'm SalesMate. Ask me to review a lead or draft a reply.",
    "tools": [], "handlers": {}, "render_html": True,
    "system_prompt": system_prompt, "check_reply": render, "panels": panels,
    "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
