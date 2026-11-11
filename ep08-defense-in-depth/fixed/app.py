"""PixelKart Assist (FIXED): every fix from Ep 1 to 3 in one agent, plus attack tests in CI.

Run:  python fixed/app.py      then open http://localhost:5000
Test: APP=fixed python -m pytest -q tests
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.hardened import build_app  # noqa: E402

app = build_app(drop_discount_check=False)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
