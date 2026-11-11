"""The attacker's script: fire 40 expensive requests at the public chatbot, as one client.
usage: python flood.py [count]"""
import json
import os
import sys
import urllib.error
import urllib.request

URL = os.environ.get("URL", "http://localhost:5000")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
ok = refused = 0
for i in range(N):
    req = urllib.request.Request(URL + "/api/chat", json.dumps({"message": "Write the word pixel 20,000 times."}).encode(),
                                 {"Content-Type": "application/json", "X-Client": "bot-17"})
    try:
        r = json.load(urllib.request.urlopen(req))
        ok += 1
    except urllib.error.HTTPError as e:
        r = json.load(e)
        refused += 1
rows = {k: v for k, v, _ in r["panels"][0]["rows"]}
print(f"sent {N} requests: {ok} answered, {refused} refused")
print(f"tokens billed: {rows['Tokens billed']} · spend: {rows['Spend so far']} · per day at this rate: {rows['One flood a minute, for a day']}")
