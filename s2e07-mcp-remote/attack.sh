#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, connects each to the same hostile MCP server,
# and prints what the bridge ran to open the login page. Nothing is really executed: PowerShell is
# simulated and commands are logged against fake outputs.
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
        r = post(base, "/api/chat", {"message": "Connect to the MCP server at toolshub.example"})
        print(f"\n=== {name.upper()} ===")
        for c in r["tool_calls"]:
            if c["name"] == "connect_server":
                print(f"[bridge] connect {c['arguments']['server']} -> 401, read OAuth metadata")
            else:
                print(f"[bridge] open login page -> {c['result']}")
        print(r["reply"])
        ran = next(x for x in r["panels"] if x["id"] == "ran")["items"]
        print("Commands run on the laptop:", [o["head"] for o in ran] or "none")
    finally:
        p.terminate()
PY
