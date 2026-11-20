"""PixelKart Assist (VULNERABLE): the same hardened agent after a "harmless" refactor that
deleted one line: the discount limit check. Nothing else changed. Code review missed it.

Run:  python vulnerable/app.py
Test: APP=vulnerable python -m pytest -q tests      (one test goes red)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.hardened import build_app  # noqa: E402

app = build_app(drop_discount_check=True)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
