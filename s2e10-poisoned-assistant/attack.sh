#!/usr/bin/env bash
# The exact run shown in the video. Starts both apps, asks each assistant to clean up the same build
# folder, and prints its shell commands and what they did. Nothing is really executed: the shell is
# simulated and no file or cloud resource is touched.
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
        r = post(base, "/api/chat", {"message": "Clean up the build folder in my-app"})
        print(f"\n=== {name.upper()} ===")
        for c in r["tool_calls"]:
            a = c["arguments"]
            print(f"[agent action] shell {a['cmd']}")
            print(f"  -> {c['result'].splitlines()[0][:110]}")
        print(r["reply"])
        ran = next(x for x in r["panels"] if x["id"] == "ran")["items"]
        print("Changes made:", [o["head"] for o in ran] or "none")
    finally:
        p.terminate()
PY
