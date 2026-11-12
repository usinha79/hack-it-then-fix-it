"""Assist (FIXED: an output check plus a permission policy on every tool call).
Run:  python fixed/app.py      then open http://localhost:5000
Compare every guardrail head to head:  python bench.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.guarded import build  # noqa: E402

app = build({"output", "policy"}, "fixed")

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
