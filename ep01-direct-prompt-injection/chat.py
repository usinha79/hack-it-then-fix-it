"""Talk to the running ShopBot from the terminal.
usage: python chat.py "your message"        (add --reset to start a fresh order first)"""
import json, os, sys, urllib.request

URL = os.environ.get("URL", "http://localhost:5000")
def post(path, body=None):
    req = urllib.request.Request(URL + path, json.dumps(body or {}).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

args = [a for a in sys.argv[1:] if a != "--reset"]
if "--reset" in sys.argv: post("/api/reset")
r = post("/api/chat", {"message": " ".join(args)})
print("ShopBot:", r["reply"].replace("\n", "\n         "))
for c in r["tool_calls"]:
    a = ", ".join(f"{k}={v}" for k, v in c["arguments"].items())
    print(f"[tool] {c['name']}({a})  {c['status'].upper()}")
o = r["order"]
print(f"[order] discount {o['discount']}%   total ₹{o['total']:,}")
