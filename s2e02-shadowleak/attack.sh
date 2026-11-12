#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, asks each for the same research report,
# and prints the agent's tool calls and what the attacker's server received. Fake data only;
# the "attacker server" is a log inside the lab, nothing leaves this machine.
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
        r = post(base, "/api/chat", {"message": "Research today's emails and give me a report."})
        print(f"\n=== {name.upper()} ===")
        for c in r["tool_calls"]:
            print(f"[agent tool call] open_url {c['arguments']['url']}")
            print(f"  -> {c['result']}")
        print(r["reply"])
        log = next(x for x in r["panels"] if x["id"] == "attacker")["items"]
        print("Attacker received:", [i["body"] for i in log] or "nothing")
    finally:
        p.terminate()
PY
