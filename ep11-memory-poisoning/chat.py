"""Talk to the running lab bot from the terminal.
usage: python chat.py "your message"
  --new    start a new chat first (the conversation is cleared, long-term memory stays)
  --wipe   wipe long-term memory first (start the lab over)"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("URL", "http://localhost:5000")


def post(path, body=None):
    req = urllib.request.Request(URL + path, json.dumps(body or {}).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


flags = {a for a in sys.argv[1:] if a.startswith("--")}
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if "--wipe" in flags:
    post("/api/wipe")
if "--new" in flags or "--wipe" in flags:
    post("/api/reset")
r = post("/api/chat", {"message": " ".join(args)})
for c in r["tool_calls"]:
    a = ", ".join(f"{k}={v!r}" for k, v in c["arguments"].items())
    print(f"[tool] {c['name']}({a})  {c['status'].upper()}")
    res = c["result"].replace("\n", " ")
    print("       → " + (res if len(res) < 110 else res[:107] + "..."))
print("Bot:", r["reply"].replace("\n", "\n     "))
