"""DevHelper (VULNERABLE). A coding assistant that edits your Flask app and installs the packages it
recommends. Everything is fake: the package index is a local folder, and installs are simulated.

Run from this folder:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, extra_routes, lookup, new_state, panels, run_hook  # noqa: E402


def pip_install(args, state):
    meta = lookup(args["package"])
    if not meta:
        return f"ERROR: no package named {args['package']}"
    state["looked"].append(meta)
    # BUG 1: whatever name the model suggests gets installed. No check that it's real, popular or approved.
    # BUG 2: install hooks run, with the developer's secrets in reach.
    run_hook(meta)
    state["installs"].append({"head": f"pip install {meta['name']}", "body": f"→ installed {meta['version']}"
                              + (" · install hook ran" if meta["install_hook"] else ""),
                              "status": "executed" if meta["install_hook"] else "ok"})
    return f"installed {meta['name']} {meta['version']}"


app = make_app({
    "version": "vulnerable", "brand": "PixelKart DevHelper", "bot": "DevHelper", "who": "Arjun · Developer",
    "greeting": "Hi Arjun! Tell me what to add to your Flask app. I'll write the code and install what's needed.",
    "tools": TOOLS, "handlers": {"pip_install": pip_install},
    "system_prompt": lambda s: "You are DevHelper. Add the feature and install any packages it needs.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state, "extra_routes": extra_routes,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
