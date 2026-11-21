"""Write the list of live Dev.to articles for this series to .github/devto-links.json.

Uses Dev.to's public API (published articles only, no key needed) and maps each
article to its episode folder by the lab link in the article body.
"""
import json
import re
import time
import urllib.request

USER = "bugbountybeyond"
OUT = ".github/devto-links.json"
HEADERS = {"User-Agent": "hack-it-then-fix-it-links", "Accept": "application/vnd.forem.api-v1+json"}


def get(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(5)


articles, page = [], 1
while True:
    batch = get(f"https://dev.to/api/articles?username={USER}&per_page=100&page={page}")
    if not batch:
        break
    articles += batch
    page += 1

links = {}
for a in articles:
    body = get(f"https://dev.to/api/articles/{a['id']}").get("body_markdown", "")
    m = re.search(r"tree/main/((?:ep|s\d+e)\d\d[a-z0-9-]*)", body)
    if not m:
        continue
    folder = m.group(1)
    links[folder] = {"title": a["title"], "url": a["url"], "published_at": a.get("published_at")}
    time.sleep(1)

with open(OUT, "w") as f:
    json.dump(dict(sorted(links.items())), f, indent=1)
    f.write("\n")
print(f"{len(links)} live articles")
