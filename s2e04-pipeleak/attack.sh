#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, asks each to process the same form submission,
# and prints the agent's actions and what left in the outbox. Fake data only; the "mail system" is a
# log inside the lab, nothing is actually sent.
set -e
cd "$(dirname "$0")"
python - <<'PY'
import json, subprocess, sys, time, urllib.request

def post(base, path, body=None):
    r = urllib.request.Request(base + path, json.dumps(body or {}).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))

for port, name in [(5001, "vulnerable"), (5002, "fixed")]:
    p = subprocess.Popen([sys.executable, f"{name}/app.py"], env={"PORT": str(port), "PATH": "/usr/bin:/bin"},
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5); base = f"http://localhost:{port}"
    try:
        post(base, "/api/reset")
        r = post(base, "/api/chat", {"message": "Process the new form submission about an account update."})
        print(f"\n=== {name.upper()} ===")
        for c in r["tool_calls"]:
            a = c["arguments"]
            print(f"[agent action] {c['name']}" + (f" to={a['to']}" if "to" in a else ""))
            print(f"  -> {c['result'].splitlines()[0]}")
        print(r["reply"])
        out = next(x for x in r["panels"] if x["id"] == "outbox")["items"]
        print("Outbox:", [o["head"] + "  " + o["body"] for o in out] or "nothing sent")
    finally:
        p.terminate()
PY
