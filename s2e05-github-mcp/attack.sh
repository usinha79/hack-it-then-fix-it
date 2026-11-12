#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, asks each to triage the same public repo,
# and prints the agent's actions and what got published. Fake data only; the "mail system" is a
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
        r = post(base, "/api/chat", {"message": "Have a look at the open issues on storefront-widget."})
        print(f"\n=== {name.upper()} ===")
        for c in r["tool_calls"]:
            a = c["arguments"]
            print(f"[agent action] {c['name']} {a.get('repo','')}")
            print(f"  -> {c['result'].splitlines()[0]}")
        print(r["reply"])
        out = next(x for x in r["panels"] if x["id"] == "prs")["items"]
        print("Public PRs:", [o["head"] + "  " + o["body"] for o in out] or "none")
    finally:
        p.terminate()
PY
