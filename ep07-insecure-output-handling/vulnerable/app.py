"""ReviewBot (VULNERABLE). An AI helper in PixelKart's admin dashboard that summarises customer reviews.
Everything is fake: the shop, the reviews, the users, the admin session.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, db, extra_routes, new_state, panels  # noqa: E402


def get_reviews(args, state):
    # BUG 1: the model's output is pasted straight into SQL.
    sql = f"SELECT author, text FROM reviews WHERE product = '{args['product']}'"
    try:
        rows = db().execute(sql).fetchall()
        state["queries"].append((sql, "executed"))
    except Exception as e:
        state["queries"].append((sql, "blocked"))
        return f"BLOCKED: {e}"
    return "\n".join(f"{a}: {t}" for a, t in rows)


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Admin", "bot": "ReviewBot", "who": "Priya · Admin",
    "greeting": "Hi Priya! Ask me to summarise reviews for any product.",
    "tools": TOOLS, "handlers": {"get_reviews": get_reviews},
    "system_prompt": lambda s: "You are ReviewBot. Summarise customer reviews, quoting customers.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
    # BUG 2: the dashboard renders the model's reply as HTML.
    "render_html": True,
    # BUG 3: the admin session cookie is readable by JavaScript.
    "cookie": ("admin_session", "LAB-FAKE-ADMIN-SESSION-8c1f", False),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
