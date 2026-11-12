"""WatchBot (FIXED: the app logs structured security events).
It runs the detection rules in detect.py over yesterday's logs of PixelKart Assist.

Run:  python fixed/app.py      then open http://localhost:5000
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.server import make_app  # noqa: E402
from common.shared import TOOLS, make  # noqa: E402

new_state, scan_logs, panels = make("security.jsonl")

app = make_app({
    "version": "fixed", "brand": "PixelKart WatchBot", "bot": "WatchBot", "who": "Security on-call",
    "greeting": "Hi! I watch PixelKart Assist's logs. Ask me if anything suspicious happened.",
    "tools": TOOLS, "handlers": {"scan_logs": scan_logs},
    "system_prompt": lambda s: "You are WatchBot. Scan the logs and summarise the alerts.",
    "check_reply": lambda r, s: (r, False), "panels": panels, "new_state": new_state,
})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), threaded=True)
