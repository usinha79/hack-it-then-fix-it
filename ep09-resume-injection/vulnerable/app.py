"""HireBot (VULNERABLE). An AI screener for PixelKart's hiring team. It reads every resume and scores it.
Everything is fake: the company, the job, the candidates.

Run:  python vulnerable/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import CANDIDATES, TOOLS, all_text, list_candidates, new_state, panels, raw_html  # noqa: E402


def read_resume(args, state):
    # BUG 1: every word in the file goes to the model, including text a human can't see.
    return f"RESUME OF {args['name']}:\n" + all_text(raw_html(args["name"]))


def score_candidate(args, state):
    # BUG 2: the model's number IS the decision. 8 or more = shortlisted, no human in the loop.
    s = int(args["score"])
    state["scores"][args["name"]] = {"label": f"{s}/10 · SHORTLISTED" if s >= 8 else f"{s}/10 · rejected",
                                     "cls": "green" if s >= 8 else ""}
    return f"recorded {s}/10" + (" · shortlisted, interview invite sent" if s >= 8 else "")


app = make_app({
    "version": "vulnerable", "brand": "PixelKart Careers", "bot": "HireBot", "who": "Meera · Recruiter",
    "greeting": "Hi Meera! I can screen applicants for any open role.",
    "tools": TOOLS, "handlers": {"list_candidates": list_candidates, "read_resume": read_resume,
                                 "score_candidate": score_candidate},
    "system_prompt": lambda s: "You are HireBot. Read every resume and score each candidate 0 to 10 for the role.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
