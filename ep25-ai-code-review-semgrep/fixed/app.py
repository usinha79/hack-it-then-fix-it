"""ReviewBot (FIXED: Semgrep rules find the bugs, in code; the model only explains them).
The merge decision comes from the scanner's findings, never from the model's words.

Run:  python fixed/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, new_state, panels, semgrep  # noqa: E402


def review_pr(args, state):
    v = args["version"]
    found = semgrep(v)
    state.update(version=v, merge_unsafe=False,
                 comments=[{"head": f"line {f['line']}  ·  {f['rule']}", "body": f"{f['code']}  —  {f['msg']}",
                            "status": "blocked" if f["sev"] == "ERROR" else "warn"} for f in found])
    errors = sum(f["sev"] == "ERROR" for f in found)
    state.update(merge="blocked" if errors else "allowed",
                 merge_why=f"{errors} blocking findings from the rule pack." if errors else "0 findings from the rule pack.")
    return f"{len(found)} findings: " + "; ".join(f"line {f['line']} {f['rule']}" for f in found)


app = make_app({
    "version": "fixed", "brand": "PixelKart ReviewBot", "bot": "ReviewBot", "who": "Engineering",
    "greeting": "Hi! I review pull requests before they merge. Ask me to review PR 42.",
    "tools": TOOLS, "handlers": {"review_pr": review_pr},
    "system_prompt": lambda s: "You are ReviewBot. Explain the scanner's findings. You do not decide the merge.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
