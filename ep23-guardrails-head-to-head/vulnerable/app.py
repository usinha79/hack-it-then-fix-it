"""Assist (VULNERABLE: protected by an input keyword blocklist only).
Run:  python vulnerable/app.py      then open http://localhost:5000
Compare every guardrail head to head:  python bench.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.guarded import build  # noqa: E402

app = build({"blocklist"}, "vulnerable")

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
