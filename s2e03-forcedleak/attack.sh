#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, asks each to review the web-form lead,
# and shows which images the browser would load. Fake data only; the "internet" is a log in the lab.
set -e
cd "$(dirname "$0")"
python - <<'PY'
import json, re, subprocess, sys, time, urllib.request

def post(base, path, body=None):
    r = urllib.request.Request(base + path, json.dumps(body or {}).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))

for port, name in [(5001, "vulnerable"), (5002, "fixed")]:
    p = subprocess.Popen([sys.executable, f"{name}/app.py"], env={"PORT": str(port), "PATH": "/usr/bin:/bin"},
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5); base = f"http://localhost:{port}"
    try:
        post(base, "/api/reset")
        r = post(base, "/api/chat", {"message": "Review the new web form lead from Northwind and suggest a next step."})
        print(f"\n=== {name.upper()} ===")
        print(r["reply"])
        for src in re.findall(r'<img src="([^"]+)"', r["reply"]):   # the browser loads it, no click
            urllib.request.urlopen(base + src).read()
        eg = next(x for x in json.load(urllib.request.urlopen(base + "/api/info"))["panels"] if x["id"] == "egress")
        print("Left the page:", [i["head"] + "  " + i["body"] for i in eg["items"]] or "nothing")
    finally:
        p.terminate()
PY
