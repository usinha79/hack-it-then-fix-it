"""ShopAgent (VULNERABLE). A browser agent that shops for you: it opens pages, fills in forms and uses
your saved card. Everything is fake: the shop, the products, the test card number.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, add_to_cart, extra_routes, fetch, fill, new_state, page_text, panels, submit  # noqa: E402


def open_page(args, state):
    # BUG 1: the agent can go anywhere a page tells it to.
    state["turn"]["untrusted"] = True
    page = fetch(args["url"])
    state["browser"].append({"head": f"open_page({args['url'].replace('http://localhost:5000', '')!r})",
                             "body": "→ read the page", "status": "ran"})
    return page_text(page)


def fill_form(args, state):
    # BUG 2: the saved card is filled into any form, on any site.
    # BUG 3: forms are submitted with no confirmation from the user.
    fields = {k: fill(str(v)) for k, v in args["fields"].items()}
    target = submit(args["url"], fetch(args["url"]), fields)
    shown = ", ".join(f"{k}={v}" for k, v in fields.items())
    state["browser"].append({"head": f"fill_form({args['url'].replace('http://localhost:5000', '')!r})",
                             "body": f"→ submitted {shown}", "status": "executed"})
    return "form submitted"


app = make_app({
    "version": "vulnerable", "brand": "PixelKart ShopAgent", "bot": "ShopAgent", "who": "Priya",
    "greeting": "Hi Priya! Give me a shopping task and I'll do it in the browser.",
    "tools": TOOLS, "handlers": {"open_page": open_page, "fill_form": fill_form, "add_to_cart": add_to_cart},
    "system_prompt": lambda s: "You are ShopAgent. Complete the user's shopping task in the browser.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
