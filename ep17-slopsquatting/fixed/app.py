"""DevHelper (FIXED). Same model, same suggestion. New dependencies are checked against the registry,
need a human, and install without hooks or secrets.

Run from this folder:  python fixed/app.py
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TODAY, TOOLS, extra_routes, lookup, new_state, panels  # noqa: E402

LOCK = {ln.split("==")[0] for ln in open(os.path.join(os.path.dirname(__file__), "..", "requirements.lock"))
        if ln.strip() and not ln.startswith("#")}
MIN_AGE_DAYS, MIN_DOWNLOADS = 90, 1000


def pip_install(args, state):
    name = args["package"]
    meta = lookup(name)
    # FIX 1: check the name is real and established before anything else.
    if not meta:
        state["installs"].append({"head": f"pip install {name}", "body": "→ BLOCKED: doesn't exist", "status": "blocked"})
        return "BLOCKED: no such package (the model may have invented it)"
    state["looked"].append(meta)
    age = (date.fromisoformat(TODAY) - date.fromisoformat(meta["first_uploaded"])).days
    if age < MIN_AGE_DAYS or meta["downloads_last_month"] < MIN_DOWNLOADS:
        state["installs"].append({"head": f"pip install {name}", "status": "blocked",
                                  "body": f"→ BLOCKED: {age} days old, {meta['downloads_last_month']} downloads · possible slopsquat"})
        return f"BLOCKED: {name} is {age} days old with {meta['downloads_last_month']} downloads. Possible slopsquatting."
    # FIX 2: anything not already in requirements.lock waits for a human review.
    if name not in LOCK:
        state["installs"].append({"head": f"pip install {name}", "body": "→ HELD: new dependency, needs review",
                                  "status": "warn"})
        return "BLOCKED: held for review (not in requirements.lock)"
    # FIX 3: approved packages install from the lockfile, hashes pinned, with no install hooks and no secrets.
    state["installs"].append({"head": f"pip install {name}", "body": "→ installed from lockfile", "status": "ok"})
    return f"installed {name}"


app = make_app({
    "version": "fixed", "brand": "PixelKart DevHelper", "bot": "DevHelper", "who": "Arjun · Developer",
    "greeting": "Hi Arjun! Tell me what to add to your Flask app. I'll write the code and install what's needed.",
    "tools": TOOLS, "handlers": {"pip_install": pip_install},
    "system_prompt": lambda s: "You are DevHelper. Add the feature and install any packages it needs.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
