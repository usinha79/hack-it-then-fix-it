"""Post the attacker's 'community answer' to the running lab's forum (it gets embedded automatically)."""
import json
import os
import urllib.request

URL = os.environ.get("URL", "http://localhost:5000")
text = open(os.path.join(os.path.dirname(__file__), "attacker_post.txt")).read().strip()
req = urllib.request.Request(URL + "/forum/post", json.dumps({"text": text}).encode(), {"Content-Type": "application/json"})
print("forum post:", json.load(urllib.request.urlopen(req))["result"])
