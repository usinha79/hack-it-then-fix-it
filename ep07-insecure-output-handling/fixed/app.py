"""ReviewBot (FIXED). Same model, same data. Model output is treated as untrusted input.

Run:  python fixed/app.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, db, extra_routes, new_state, panels  # noqa: E402


def get_reviews(args, state):
    # FIX 1: parameterised query. The model's text is a value, never part of the SQL.
    sql = "SELECT author, text FROM reviews WHERE product = ?"
    rows = db().execute(sql, (args["product"],)).fetchall()
    state["queries"].append((f"{sql}   [param: {args['product']!r}]", "ok"))
    return "\n".join(f"{a}: {t}" for a, t in rows)


app = make_app({
    "version": "fixed", "brand": "PixelKart Admin", "bot": "ReviewBot", "who": "Priya · Admin",
    "greeting": "Hi Priya! Ask me to summarise reviews for any product.",
    "tools": TOOLS, "handlers": {"get_reviews": get_reviews},
    "system_prompt": lambda s: "You are ReviewBot. Summarise customer reviews, quoting customers.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
    # FIX 2: render the model's reply as plain text (the browser escapes it).
    "render_html": False,
    # FIX 3: the session cookie is HttpOnly, so scripts can't read it even if one slips through.
    "cookie": ("admin_session", "LAB-FAKE-ADMIN-SESSION-8c1f", True),
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
