#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, sends one question to each, and shows
# what leaves the browser. Fake data only; the "internet" is all localhost.
set -e
cd "$(dirname "$0")"
python - <<'PY'
import json, re, subprocess, sys, time, urllib.request, urllib.error

def start(path, port):
    p = subprocess.Popen([sys.executable, path], env={"PORT": str(port), "PATH": "/usr/bin:/bin"},
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5); return p

def post(base, path, body=None):
    r = urllib.request.Request(base + path, json.dumps(body or {}).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))

for port, name in [(5001, "VULNERABLE"), (5002, "FIXED")]:
    proc = start(f"{'vulnerable' if port==5001 else 'fixed'}/app.py", port)
    base = f"http://localhost:{port}"
    try:
        post(base, "/api/reset")
        r = post(base, "/api/chat", {"message": "What needs my attention today?"})
        print(f"\n=== {name} ===")
        print(r["reply"])
        for src in re.findall(r'<img src="([^"]+)"', r["reply"]):  # browser auto-fetch
            try: code = urllib.request.urlopen(base + src).getcode()
            except urllib.error.HTTPError as e: code = e.code
            print(f"[browser auto-fetched] {src} -> {code}")
        eg = [p for p in json.load(urllib.request.urlopen(base + "/api/info"))["panels"] if p["id"] == "egress"][0]
        print("Outbound:", [i["head"] for i in eg["items"]] or eg["empty"])
    finally:
        proc.terminate()
PY
