"""Talk to the running lab bot from the terminal.
usage: python chat.py "your message"        (add --reset to start fresh first)"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("URL", "http://localhost:5000")


def post(path, body=None):
    req = urllib.request.Request(URL + path, json.dumps(body or {}).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


args = [a for a in sys.argv[1:] if a != "--reset"]
if "--reset" in sys.argv:
    post("/api/reset")
r = post("/api/chat", {"message": " ".join(args)})
for c in r["tool_calls"]:
    a = ", ".join(f"{k}={v!r}" for k, v in c["arguments"].items())
    print(f"[tool] {c['name']}({a})  {c['status'].upper()}")
    res = c["result"].replace("\n", " ")
    print("       → " + (res if len(res) < 110 else res[:107] + "..."))
print("Bot:", r["reply"].replace("\n", "\n     "))
